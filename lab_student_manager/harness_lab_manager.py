# Variables Panel (my honest method to organize the required env vars from a single place)
import os
import logging
import sys
import time

import requests

from lab_student_manager.custom_exceptions import HarnessAPIResultsFailure

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

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_DB = os.getenv("AIRTABLE_TABLE_DB")
HARNESS_ACCOUNT_ID = "zHadgwdTQqWG8CA3Jv6Feg"
HARNESS_ORG_ID = "P190"
HARNESS_DEFAULT_PROJECT_ID = "p1901"
HARNESS_PAT = 'pat.zHadgwdTQqWG8CA3Jv6Feg.64529572caee7a13df284306.OxTUM7XoIovAGnaLxUTs'
HARNESS_API_PATH = "https://app.harness.io/gateway/pipeline/api/"
HARNESS_SERVICE_ENV_API_PATH = "https://app.harness.io/gateway/ng/api/"
HARNESS_EMAIL_DOMAIN = "@harness.labs"


def get_pipelines_in_project(project_id):
    url = "{0}pipelines/list".format(HARNESS_API_PATH)
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "page": "0", "size": "50"}
    payload = '{"filterType": "PipelineSetup"}'

    try:
        logging.info("Loading all Pipelines from the target Harness Project...")
        results = requests.post(url=url, headers=headers, data=payload, params=parameters)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)

    # validating is the hit is good, not only the requests aspects
    if results.json()['status'] != "SUCCESS":
        raise HarnessAPIResultsFailure

    logging.info("Done!")
    return results


def delete_all_pipelines_in_project(project_id):
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    existing_pipelines = get_pipelines_in_project(project_id).json()['data']['content']
    pipeline_ids = [prj_id['identifier'] for prj_id in existing_pipelines]
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id}

    for pipeline in pipeline_ids:
        delete_url = "{0}pipelines/{1}".format(HARNESS_API_PATH, pipeline)

        try:
            logging.info("Going to delete this pipeline now: {}".format(pipeline))
            x = requests.delete(delete_url, headers=headers, params=parameters)
            logging.info(x.text)
        except requests.exceptions.RequestException as e:
            logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
            raise SystemExit(e)


def get_services_in_project(project_id):
    url = "{0}servicesV2".format(HARNESS_SERVICE_ENV_API_PATH)
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "page": "0", "size": "100",
                  "includeAllServicesAccessibleAtScope": "false"}

    try:
        logging.info("Loading all Services from the target Harness Project...")
        results = requests.get(url=url, headers=headers, params=parameters)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)

    # validating is the hit is good, not only the requests aspects
    if results.json()['status'] != "SUCCESS":
        raise HarnessAPIResultsFailure

    logging.info("Done!")
    return results


def delete_all_services_in_project(project_id):
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    existing_services = get_services_in_project(project_id).json()['data']['content']
    print(existing_services)

    service_ids = [svc_id['service']['identifier'] for svc_id in existing_services]
    print(service_ids)

    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "forceDelete": "true"}

    for svc in service_ids:
        delete_url = "{0}servicesV2/{1}".format(HARNESS_SERVICE_ENV_API_PATH, svc)

        try:
            logging.info("Going to delete this service now: {}".format(svc))
            x = requests.delete(delete_url, headers=headers, params=parameters)
            logging.info(x.text)
        except requests.exceptions.RequestException as e:
            logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
            raise SystemExit(e)


def get_environments_in_project(project_id):
    url = "{0}environmentsV2".format(HARNESS_SERVICE_ENV_API_PATH)
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "page": "0", "size": "100"}

    try:
        logging.info("Loading all Environments from the target Harness Project...")
        results = requests.get(url=url, headers=headers, params=parameters)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)

    # validating is the hit is good, not only the requests aspects
    if results.json()['status'] != "SUCCESS":
        raise HarnessAPIResultsFailure

    logging.info("Done!")
    return results


def delete_all_environments_in_project(project_id):
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    existing_environments = get_environments_in_project(project_id).json()['data']['content']

    environment_ids = [svc_id['environment']['identifier'] for svc_id in existing_environments]
    print(environment_ids)

    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "forceDelete": "true"}

    for env in environment_ids:
        delete_url = "{0}environmentsV2/{1}".format(HARNESS_SERVICE_ENV_API_PATH, env)

        try:
            logging.info("Going to delete this service now: {}".format(env))
            x = requests.delete(delete_url, headers=headers, params=parameters)
            logging.info(x.text)
        except requests.exceptions.RequestException as e:
            logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
            raise SystemExit(e)


def get_k8s_connectors_in_project(project_id):
    url = "{0}connectors/listV2".format(HARNESS_SERVICE_ENV_API_PATH)
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    payload = '''{
        "types": [
          "K8sCluster"
        ],
        "categories": [
          "CLOUD_PROVIDER"
        ],
        "inheritingCredentialsFromDelegate": true,
        "connectorConnectivityModes": [
          "DELEGATE"
        ],
        "filterType": "Connector"
    }'''
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "page": "0", "size": "100"}

    try:
        logging.info("Loading all K8s Connectors from the target Harness Project...")
        results = requests.post(url=url, headers=headers, params=parameters, data=payload)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)

    # validating is the hit is good, not only the requests aspects
    if results.json()['status'] != "SUCCESS":
        raise HarnessAPIResultsFailure

    logging.info("Done!")
    return results


def delete_all_k8s_connectors_in_project(project_id):
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    existing_connectors = get_k8s_connectors_in_project(project_id).json()['data']['content']

    environment_ids = [svc_id['connector']['identifier'] for svc_id in existing_connectors]

    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "forceDelete": "true"}

    for env in environment_ids:
        delete_url = "{0}connectors/{1}".format(HARNESS_SERVICE_ENV_API_PATH, env)

        try:
            logging.info("Going to delete this connector now: {}".format(env))
            x = requests.delete(delete_url, headers=headers, params=parameters)
            logging.info(x.text)
        except requests.exceptions.RequestException as e:
            logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
            raise SystemExit(e)


def get_delegate_tokens_in_project(project_id):
    url = "{0}delegate-token-ng".format(HARNESS_SERVICE_ENV_API_PATH)
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "status": "ACTIVE"}

    try:
        logging.info("Loading all Delegate Tokens from the target Harness Project...")
        results = requests.get(url=url, headers=headers, params=parameters)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)

    ## validating is the hit is good, not only the requests aspects
    # if results.json()['resource'] != "SUCCESS":
    #    raise HarnessAPIResultsFailure

    logging.info("Done!")

    return results


def get_delegate_groups_using_a_specific_token(project_id, delegate_token_name):
    url = "{0}delegate-token-ng/delegate-groups".format(HARNESS_SERVICE_ENV_API_PATH)
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "projectIdentifier": project_id, "delegateTokenName": delegate_token_name}

    try:
        logging.info("Loading all Delegate Tokens from the target Harness Project...")
        results = requests.get(url=url, headers=headers, params=parameters)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)

    ## validating is the hit is good, not only the requests aspects
    # if results.json()['resource'] != "SUCCESS":
    #    raise HarnessAPIResultsFailure

    logging.info("Done!")

    return results


def delete_project_by_id(project_id):
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}

    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID}

    delete_url = "{0}projects/{1}".format(HARNESS_SERVICE_ENV_API_PATH, project_id)

    try:
        logging.info("Going to delete this Project now: {}".format(project_id))
        x = requests.delete(delete_url, headers=headers, params=parameters)
        logging.info(x.text)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)


def create_project_by_id(project_id):
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID}
    create_url = "{0}projects".format(HARNESS_SERVICE_ENV_API_PATH)

    payload = '''{{
      "project": {{
        "orgIdentifier": "{org_id}",
        "identifier": "{prj_id}",
        "name": "{prj_id}",
        "description": "Powered by Gabs the Creator automations.",
        "tags": {{
          "automated": "yes",
          "owner": "gabslabs"
        }}
      }}
    }}'''.format(org_id=HARNESS_ORG_ID, prj_id=project_id)

    try:
        logging.info("Going to create this Project now: {}".format(project_id))
        x = requests.post(create_url, headers=headers, params=parameters, data=payload)
        logging.info(x.text)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)


def invite_user_to_project_by_id(project_id):
    headers = {'Content-Type': 'application/json', 'x-api-key': HARNESS_PAT}
    parameters = {"accountIdentifier": HARNESS_ACCOUNT_ID, "orgIdentifier": HARNESS_ORG_ID,
                  "routingId": HARNESS_ACCOUNT_ID, "projectIdentifier": project_id}
    create_url = "{0}user/users".format(HARNESS_SERVICE_ENV_API_PATH)
    student_owner_email = "{0}{1}".format(project_id, HARNESS_EMAIL_DOMAIN)

    payload = '''{{
    "emails": [
        "{prj_student_owner}"
    ],
    "userGroups": [
        "_project_all_users"
    ],
    "roleBindings": [
        {{
            "resourceGroupIdentifier": "_all_project_level_resources",
            "roleIdentifier": "_project_admin",
            "roleName": "Project Admin",
            "resourceGroupName": "All Project Level Resources",
            "managedRole": true
        }}
    ]
    }}'''.format(prj_student_owner=student_owner_email)

    try:
        logging.info("Going to invite the owner student to this Project now: {}".format(project_id))
        x = requests.post(create_url, headers=headers, params=parameters, data=payload)
        logging.info(x.text)
    except requests.exceptions.RequestException as e:
        logging.error("Something is wrong with the request itself, that's not even evaluating the response yet.")
        raise SystemExit(e)
    return x


def main():
    # delete_all_pipelines_in_project(project_id=HARNESS_DEFAULT_PROJECT_ID)
    # delete_all_services_in_project(project_id=HARNESS_DEFAULT_PROJECT_ID)
    # delete_all_environments_in_project(project_id=HARNESS_DEFAULT_PROJECT_ID)
    # delete_all_k8s_connectors_in_project(project_id=HARNESS_DEFAULT_PROJECT_ID)
    # print(get_delegate_groups_using_a_specific_token(project_id=HARNESS_DEFAULT_PROJECT_ID, delegate_token_name="instruqt").text)
    #elete_project_by_id("p1904")
    #time.sleep(3)
    #create_project_by_id("p1904")
    #time.sleep(3)
    #invite_user_to_project_by_id("p1904")
    print("Nothing to see here...")


if __name__ == '__main__':
    main()
