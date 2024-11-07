import requests
import json
import time
from datetime import date, datetime

requests.packages.urllib3.disable_warnings()

ome_ip = 'o_ip'
vcenter_username = 'v_user'
vcenter_password = 'v_pass'
vcenter_cluster_name = 'v_cluster'

def get_console_uuid() -> str:
    url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles"
    response = requests.get(url, verify=False, auth=(vcenter_username, vcenter_password))
    uuid = response.json()[0]["uuid"]
    print(f'Captured Console UUID: {uuid}')
    return uuid

def resync_repo_profiles() -> str:
    url = f"https://{ome_ip}/omevv/GatewayService/v1/RepositoryProfiles/ResyncRepository"

    payload = json.dumps({})
    headers = {'x_omivv-api-vcenter-identifier': uuid, 'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=payload, verify=False, auth=(vcenter_username, vcenter_password))
    if response.status_code == 202:
        print("Successfully initiated a repository resync which should complete in a few moments")
        time.sleep(300)
    else:
        raise Exception(f"Repository failed with status code: {response.status_code}")
    
def get_repo_id() -> str:
    url = "https://demo-omevv-02-ome.ose.adc.delllabs.net/omevv/GatewayService/v1/RepositoryProfiles"
    headers = {'x_omivv-api-vcenter-identifier': uuid}
    start_string = 'API Created Repository'
    response = requests.get(url, headers=headers, auth=(vcenter_username, vcenter_password), verify=False)
    response_json = response.json()

    if response.status_code == 200:
        print('Retrieving repo data and capturing repository Id')
    
    for each in response_json:
        if each['profileName'].startswith(start_string):
            repo_id = each['id']
    print(f'Setting repository Id to {repo_id}')
    return repo_id

def get_cluster_id() -> str:
    url = f"https://demo-omevv-02-ome.ose.adc.delllabs.net/omevv/GatewayService/v1/Consoles/{uuid}/Groups"
    payload = {}
    headers = {'x_omivv-api-vcenter-identifier': uuid}
    response = requests.get(url, headers=headers, auth=(vcenter_username, vcenter_password), verify=False)
    response_json = response.json()

    if response.status_code == 200:
        print('Retrieving cluster data and capturing VMware cluster id')
    
    for each in response_json:
        consoleEntityName = each['consoleEntityName']
        if consoleEntityName == vcenter_cluster_name:
            print(f'Captured VMware cluster id of {each["groupId"]}')
            return each['groupId']

def create_baseline() -> str:
    url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles/{uuid}/BaselineProfiles"
    f_now = datetime.now().strftime("%d%m%y %H%M%S")
    payload = json.dumps({
    "name": f"API Created Baseline {f_now}",
    "description": f"API Created Baseline {f_now}",
    "firmwareRepoId": repo_id,
    "driverRepoId": None,
    "configurationRepoId": None,
    "createdBy": "rob_smith1@ose.local",
    "groupIds": [
        cluster_id
    ],
    "jobSchedule": {
        "monday": True,
        "tuesday": True,
        "wednesday": True,
        "thursday": True,
        "friday": True,
        "saturday": True,
        "sunday": True,
        "time": "05:30"
    }
    })
    headers = {'x_omivv-api-vcenter-identifier': uuid, 'Content-Type': 'application/json'    }

    response = requests.post(url, headers=headers, data=payload, auth=(vcenter_username, vcenter_password), verify=False)
    if response.status_code == 200:
        print("Successfully created requested baseline")
    else:
        print(response.text)
        raise Exception(f"Baseline failed with status code: {response.status_code}")

uuid = get_console_uuid()
#resync_repo_profiles()
cluster_id = get_cluster_id()
repo_id = get_repo_id()
create_baseline()