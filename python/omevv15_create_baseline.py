import requests
import json
import time
from datetime import datetime

requests.packages.urllib3.disable_warnings()

ome_ip = '' #openmanage enterprise ip or fqdn
vcenter_username = ''
vcenter_password = ''
vcenter_cluster_name = ''   #name of vcenter cluster to be tied to the new baseline
profile_name_prefix = 'API Created' #used to filter for baseline profiles that start with this name and created by create_vsan_repo.py

def get_console_uuid() -> str:
    url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles"
    response = requests.get(url, verify=False, auth=(vcenter_username, vcenter_password))
    uuid = response.json()[0]["uuid"]
    print(f'Captured vCenter console ID ({uuid})')
    return uuid

def resync_repo_profiles() -> str:
    url = f"https://{ome_ip}/omevv/GatewayService/v1/RepositoryProfiles/ResyncRepository"

    payload = json.dumps({})
    headers = {'x_omivv-api-vcenter-identifier': uuid, 'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=payload, verify=False, auth=(vcenter_username, vcenter_password))
    if response.status_code == 202:
        print("Successfully initiated a repository resync which should complete in a few moments")
        time.sleep(300) #pause five minutes for resync to complete
    else:
        raise Exception(response.text)

def get_most_recent_repo_id() -> int:
    url = "https://demo-omevv-02-ome.ose.adc.delllabs.net/omevv/GatewayService/v1/RepositoryProfiles"
    headers = {'x_omivv-api-vcenter-identifier': uuid}
    response = requests.get(url, headers=headers, auth=(vcenter_username, vcenter_password), verify=False)
    response_json = response.json()
    matching_profiles = [profile for profile in response_json if profile['profileName'].startswith(profile_name_prefix)]
    
    if not matching_profiles:
        raise Exception(f"No profiles found starting with '{profile_name_prefix}'")
        return None
    
    most_recent_profile = max(matching_profiles, key=lambda x: datetime.fromisoformat(x['catalogCreatedDate'][:-1]))
    print(f"Identified target repository ID ({most_recent_profile['id']})")
    return most_recent_profile['id']

def get_cluster_id() -> int:
    url = f"https://demo-omevv-02-ome.ose.adc.delllabs.net/omevv/GatewayService/v1/Consoles/{uuid}/Groups"
    headers = {'x_omivv-api-vcenter-identifier': uuid}
    response = requests.get(url, headers=headers, auth=(vcenter_username, vcenter_password), verify=False)
    response_json = response.json()
    #print(url)
    if response.status_code == 200:
        print('Retrieving cluster data to find VMware cluster ID')
    else:
        raise Exception(response.text)
    
    for each in response_json:
        consoleEntityName = each['consoleEntityName']
        if consoleEntityName == vcenter_cluster_name:
            print(f'Captured VMware cluster ID ({each["groupId"]})')
            return each['groupId']
    raise Exception(f"vCenter cluster '{vcenter_cluster_name}' not found")

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
    headers = {'x_omivv-api-vcenter-identifier': uuid, 'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=payload, auth=(vcenter_username, vcenter_password), verify=False)
    payload_json = json.loads(payload)
    baseline_name = payload_json['name']

    if response.status_code == 200:
        print(f"Successfully created requested baseline ({baseline_name})")
    else:
        raise Exception(response.text)

uuid = get_console_uuid()
#resync_repo_profiles()
repo_id = get_most_recent_repo_id()
cluster_id = get_cluster_id()
create_baseline()