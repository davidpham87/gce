import os
import storm # ssh
import time
from dotenv.main import DotEnv, find_dotenv

import google.auth
from google.oauth2 import service_account
import googleapiclient.discovery

def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)

USER_VARIABLES  = DotEnv(find_dotenv()).dict()
GCE_JSON_CERT = os.path.join(os.getcwd(), USER_VARIABLES['GCE_JSON_CERT'])
GCE_PROJECT_NAME = USER_VARIABLES['GCE_PROJECT_NAME']
GCE_ZONE = USER_VARIABLES['GCE_ZONE']
GCE_USER = USER_VARIABLES['GCE_USER']

credentials = service_account.Credentials.from_service_account_file(GCE_JSON_CERT)
compute = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

result = compute.instances().list(project=GCE_PROJECT_NAME, zone=GCE_ZONE).execute()
instance_name = result['items'][0]['name']
request_id = compute.instances().stop(project=GCE_PROJECT_NAME, zone=GCE_ZONE, instance=instance_name).execute()
wait_for_operation(compute, GCE_PROJECT_NAME, GCE_ZONE, request_id['name'])

result = compute.instances().list(project=GCE_PROJECT_NAME, zone=GCE_ZONE).execute()


