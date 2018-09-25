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
request_id = compute.instances().start(project=GCE_PROJECT_NAME, zone=GCE_ZONE, instance=instance_name).execute()
wait_for_operation(compute, GCE_PROJECT_NAME, GCE_ZONE, request_id['name'])

result = compute.instances().list(project=GCE_PROJECT_NAME, zone=GCE_ZONE).execute()
ip_address = result['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP']

ssh_config = storm.Storm()

if not ssh_config.is_host_in('gce'):
    ssh_config.add_entry(
        'gce', ip_address, GCE_USER, '~/.ssh/id_rsa.pub', 22)
else:
    ssh_config.update_entry('gce', hostname=ip_address)

if not ssh_config.is_host_in('gce-jupyter'):
    ssh_config.add_entry(
        'gce-jupyter', ip_address, GCE_USER,
        22, '~/.ssh/id_rsa.pub', [('localforward', '8000 localhost:8888')])
else:
    ssh_config.update_entry('gce-jupyter', hostname=ip_address,
                            localforward='8000 localhost:8888')

print("Connect via")
print('ssh gce')

launch_jupyter = ' '.join([
    'ssh gce "jupyter notebook --port=8888"'])

print('''Connect to it:
ssh gce-jupyter
Enter this in a browser:
https://{}:8888/
Or alternatively
https://localhost:8000/'''.format(ip_address))


