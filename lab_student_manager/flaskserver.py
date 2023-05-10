import os
import time

from flask import Flask, request
from flask_basicauth import BasicAuth
import sys
import logging
import airtable_data_manager
import harness_lab_manager
from lab_student_manager import vault_manager
from lab_student_manager.student import Student
from featureflags.client import CfClient
from featureflags.evaluations.auth_target import Target
from featureflags.config import with_base_url, with_events_url

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_DB = os.getenv("AIRTABLE_TABLE_DB")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
VAULT_SERVER_URL = os.getenv("VAULT_SERVER_URL")
VAULT_SECRET_MOUNTPOINT = os.getenv("VAULT_SECRET_MOUNTPOINT")
VAULT_SECRET_PATH = os.getenv("VAULT_SECRET_PATH")
HARDCODED_PWD = os.getenv("HARDCODED_PWD")

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = os.getenv("FLASK_API_USER")
app.config['BASIC_AUTH_PASSWORD'] = os.getenv("FLASK_API_PWD")

basic_auth = BasicAuth(app)

# HARNESS FEATURE FLAG PANEL
api_key = '4768ccc4-b34d-4057-9913-fba6f5431df6'
client = CfClient(api_key,
                  with_base_url("https://config.ff.harness.io/api/1.0"),
                  with_events_url("https://events.ff.harness.io/api/1.0"))
target = Target(identifier="flask_gabs", name="flaskgabs")

# Logging configuration
# file_handler = logging.FileHandler(filename='tmp.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
# handlers = [file_handler, stdout_handler]
handlers = [stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)


def get_final_student_object(at_token, at_base_id, at_table_db, vault_token, vault_server_url, vault_secret_mountpoint,
                             vault_secret_path):
    """
    Here we'll build the final Student Object to be shared as the output of this lil automation

    :return: JSON as STRING
    """
    final_student_slot = {}

    # FF Evaluation to know if I should skip Vault
    skip_vault_bool = client.bool_variation('skip_vault', target, False)
    logging.info("DEBUG GABS: Result %s", skip_vault_bool)

    if skip_vault_bool:
        current_pwd = HARDCODED_PWD
    else:
        # First we try to get the password. Without it, we can't do anything else
        # TODO ADD a try catch with logging
        current_pwd = vault_manager.get_student_password(vault_token=vault_token, vault_server_url=vault_server_url,
                                                         vault_secret_mountpoint=vault_secret_mountpoint,
                                                         vault_secret_path=vault_secret_path)

    # Then we get the student meta from AirTable
    lab_student_from_DB = airtable_data_manager.get_and_reserve_one_slot(at_token=at_token, at_base_id=at_base_id,
                                                                         at_table_db=at_table_db)

    # Then we build our dict and cast it properly
    student_obj = Student(email=lab_student_from_DB['fields']['email'], password=current_pwd,
                          harness_project=lab_student_from_DB['fields']['harness_project'], is_taken=1)

    return student_obj


def bounce_the_student_project_by_id(project_id):
    logging.info("Starting to bounce the entire {0} Project...")
    harness_lab_manager.delete_project_by_id(project_id)
    time.sleep(1)
    harness_lab_manager.create_project_by_id(project_id)
    time.sleep(1)
    harness_lab_manager.invite_user_to_project_by_id(project_id)
    logging.info("Done!")


def wrap_up_end_free_student_slot_by_id(project_id, at_table_db, at_token, at_base_id):
    logging.info(
        "You are in the wrap up mechanism. We'll recreate your project and free the slot. ID: {0}".format(project_id))
    bounce_the_student_project_by_id(project_id)
    logging.info(
        "Time to free the slot ID: {0} in AirTable".format(project_id))
    airtable_data_manager.mark_student_as_free(student_id=project_id, at_table_db=at_table_db, at_token=at_token,
                                               at_base_id=at_base_id)


@app.route('/')
def index():
    return "I'm alive!"


@app.route('/secret')
@basic_auth.required
def secret_view():
    return {"Secret": "Voldemort"}


@app.route("/user-slot")
@basic_auth.required
def user_slot():
    results = get_final_student_object(
        at_token=AIRTABLE_TOKEN,
        at_base_id=AIRTABLE_BASE_ID, at_table_db=AIRTABLE_TABLE_DB,
        vault_token=VAULT_TOKEN,
        vault_server_url=VAULT_SERVER_URL,
        vault_secret_mountpoint=VAULT_SECRET_MOUNTPOINT,
        vault_secret_path=VAULT_SECRET_PATH
    )
    return str(results)


@app.route("/bounce-project")
@basic_auth.required
def bounce_project():
    target_project = request.args.get('prjId')
    if target_project is None:
        logging.info("You forgot to mention the prjId param in the URL. For example, ?prjId=p1901")
        message = "You forgot to mention the prjId param in the URL. For example, ?prjId=p1901"
    else:
        bounce_the_student_project_by_id(target_project)
        message = "The {0} Project is brand new now!".format(target_project)

    return message


@app.route("/full-wrap-up")
@basic_auth.required
def full_wrap_up():
    target_project = request.args.get('prjId')
    if target_project is None:
        logging.info("You forgot to mention the prjId param in the URL. For example, ?prjId=p1901")
        message = "You forgot to mention the prjId param in the URL. For example, ?prjId=p1901"
    else:
        wrap_up_end_free_student_slot_by_id(project_id=target_project, at_table_db=AIRTABLE_TABLE_DB,
                                            at_token=AIRTABLE_TOKEN,
                                            at_base_id=AIRTABLE_BASE_ID)
        message = "The {0} slot is free for use!".format(target_project)

    return message


if __name__ == "__main__":
    app.run()
