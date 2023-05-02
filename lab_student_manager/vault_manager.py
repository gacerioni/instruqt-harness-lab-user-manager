import logging
import hvac
from custom_exceptions import VaultConnFailure, VaultQueryFailure


def get_hvac_conn(vault_token, vault_server_url):
    logging.info("Getting the Vault Connection Client...")
    try:
        client = hvac.Client(url=vault_server_url)
        client.token = vault_token

        if not client.is_authenticated():
            logging.error("It seems that the vault connection is failing")
            raise VaultConnFailure("Vault Connection Failure")

    except VaultConnFailure:
        logging.error("Exception Handler - The program will raise this exception to not hide any issues.")
        raise
    else:
        logging.info("Vault Connection Client is ready!")

    return client


def get_student_password(vault_token, vault_server_url, email="p1901@harness.labs", vault_secret_mountpoint="kv-v2",
                         vault_secret_path="lab"):
    # getting the vault conn object
    conn_client = get_hvac_conn(vault_token, vault_server_url)

    try:
        # Getting the current PWD
        read_pwd_response = conn_client.secrets.kv.read_secret_version(mount_point=vault_secret_mountpoint,
                                                                       path=vault_secret_path)
        if type(read_pwd_response) is not dict:
            logging.error("The Vault query did not return a dict, something is wrong with the integration.")
            raise VaultQueryFailure

        final_pwd = read_pwd_response['data']['data']['harness_password']
    except VaultQueryFailure:
        logging.error("Exception Handler - The program will raise this exception to not hide any issues.")
        raise
    else:
        logging.info("Vault Query is OK!")

    return final_pwd
