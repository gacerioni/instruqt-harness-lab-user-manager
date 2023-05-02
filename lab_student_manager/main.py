import os
import sys
import logging
import airtable_data_manager
import vault_manager
from student import Student

# Logging configuration
#file_handler = logging.FileHandler(filename='tmp.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
# handlers = [file_handler, stdout_handler]
handlers = [stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

# Variables Panel (my honest method to organize the required env vars from a single place)
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_DB = os.getenv("AIRTABLE_TABLE_DB")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
VAULT_SERVER_URL = os.getenv("VAULT_SERVER_URL")
VAULT_SECRET_MOUNTPOINT = os.getenv("VAULT_SECRET_MOUNTPOINT")
VAULT_SECRET_PATH = os.getenv("VAULT_SECRET_PATH")


def get_final_student_object():
    """
    Here we'll build the final Student Object to be shared as the output of this lil automation

    :return: JSON as STRING
    """
    final_student_slot = {}

    # First we try to get the password. Without it, we can't do anything else
    # TODO ADD a try catch with logging
    current_pwd = vault_manager.get_student_password(vault_token=VAULT_TOKEN, vault_server_url=VAULT_SERVER_URL, vault_secret_mountpoint=VAULT_SECRET_MOUNTPOINT, vault_secret_path=VAULT_SECRET_PATH)

    # Then we get the student meta from AirTable
    lab_student_from_DB = airtable_data_manager.get_and_reserve_one_slot(at_token=AIRTABLE_TOKEN, at_base_id=AIRTABLE_BASE_ID, at_table_db=AIRTABLE_TABLE_DB)

    # Then we build our dict and cast it properly
    student_obj = Student(email=lab_student_from_DB['fields']['email'], password=current_pwd,
                          harness_project=lab_student_from_DB['fields']['harness_project'], is_taken=1)

    return student_obj


def main():
    logging.info("Lets get a fresh student for you")

    print("This is your student credential details for the lab:")
    final_output = get_final_student_object()
    print(final_output)
    logging.info("Exiting now...")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
