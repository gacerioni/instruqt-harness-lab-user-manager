import os

from flask import Flask
import airtable_data_manager
from lab_student_manager import vault_manager
from lab_student_manager.student import Student

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_DB = os.getenv("AIRTABLE_TABLE_DB")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
VAULT_SERVER_URL = os.getenv("VAULT_SERVER_URL")
VAULT_SECRET_MOUNTPOINT = os.getenv("VAULT_SECRET_MOUNTPOINT")
VAULT_SECRET_PATH = os.getenv("VAULT_SECRET_PATH")

app = Flask(__name__)


def get_final_student_object(at_token, at_base_id, at_table_db, vault_token, vault_server_url, vault_secret_mountpoint,
                             vault_secret_path):
    """
    Here we'll build the final Student Object to be shared as the output of this lil automation

    :return: JSON as STRING
    """
    final_student_slot = {}

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


@app.route("/user-slot")
def index():
    results = get_final_student_object(
        at_token=AIRTABLE_TOKEN,
        at_base_id=AIRTABLE_BASE_ID, at_table_db=AIRTABLE_TABLE_DB,
        vault_token=VAULT_TOKEN,
        vault_server_url=VAULT_SERVER_URL,
        vault_secret_mountpoint=VAULT_SECRET_MOUNTPOINT,
        vault_secret_path=VAULT_SECRET_PATH
    )
    return str(results)


if __name__ == "__main__":
    app.run()
