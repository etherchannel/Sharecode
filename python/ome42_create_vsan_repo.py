#This script will create a vsan firmware repository in openmanage enterprise based on the user defined catalog version. 

import requests, json
from datetime import date, datetime

requests.packages.urllib3.disable_warnings()

ome_ip = '172.26.38.195'                 #openmanage enterprise ip or fqdn
ome_username = 'admin'
ome_password = 'P@ssw0rd'
#catalog_type = 'vSAN Catalog for Enterprise Servers'
catalog_type = 'ESXi Catalog for Enterprise Servers'
catalog_version = "21.11.15" #https://www.dell.com/support/kbdoc/en-us/000225254/firmware-catalog-for-dell-s-vsan-ready-nodes-with-esxi-8-x-branch-images
repo_name_prefex = 'API Created Repository' #will be appended with date and time
baseline_name_prefex = 'API Created Baseline' #will be appended with date and time

def get_auth_token() -> str:
    """Get an authentication token from OpenManage Enterprise."""
    auth_url = f"https://{ome_ip}/api/SessionService/Sessions"
    auth_headers = {"Content-Type": "application/json"}
    auth_payload = {
        "UserName": ome_username, 
        "Password": ome_password, 
        "SessionType": "API"
        }
    response = requests.post(auth_url, headers=auth_headers, data=json.dumps(auth_payload), verify=False, auth=(ome_username, ome_password))
    if response.status_code == 201:
        print("Authenticated to OpenManage Enterprise")
        return response.headers["X-Auth-Token"]        
    raise Exception(response.text)

def get_catalog_id() -> str:
    catalog_url = f"https://{ome_ip}/api/UpdateManagementService/Catalogs"
    headers = {
        "Content-Type": "application/json", 
        "X-Auth-Token": token
        }
    response = requests.get(catalog_url, headers=headers, verify=False)
    response_json = response.json()
    if response.status_code == 200:
        print('Parsing online firmware catalog data')
    else:
        raise Exception(response.text)
    vsan_catalog_items = []
    for catalog in response_json['value']:
        if catalog['Key'].startswith("Index Catalog"):
            for item in catalog['Value']:
                if item['Key'] == catalog_type:
                    for vsan_item in item['Value']:
                        if vsan_item['Key'] == catalog_version:  
                            vsan_catalog_items.append(vsan_item)
                            vsan_catalog_id = vsan_item['Id'] 
                            print(f'Found user defined catalog version ({catalog_version})')  
                            return vsan_catalog_id
    raise Exception(f"vSAN firmware catalog '{catalog_version}' not found")

def get_group_id() -> int:
    server_group_url = f"https://{ome_ip}/api/GroupService/Groups"
    headers = {
        "Content-Type": "application/json", 
        "X-Auth-Token": token
        }
    response = requests.get(server_group_url, headers=headers, verify=False)
    response_json = response.json()
    if response.status_code == 200:
        print('Retrieving group data')
    else:
        raise Exception(response.text)
    for each in response_json['value']:
        name = each['Name']
        if name == 'All Devices':
            grp_id = each['Id']
            print(f'Identified the required ID ({grp_id}) from the \'All Devices\' group')
            return grp_id

def create_repo():
    repo_url = f"https://{ome_ip}/api/UpdateManagementService/Repositories"
    now = datetime.now()
    f_now = now.strftime("%d%m%y %H%M%S")
    repo_payload = json.dumps({
        "BaseCatalogID": f"{catalog_id}",
        "BaseCatalogName": f"Index Catalog-{catalog_version}",
        "Name": f"{repo_name_prefex} {f_now}",
        "DeviceSelectionType": "groups",
        "BaselineName": f"{baseline_name_prefex} {f_now}",
        "IsBaseline": True,
        "GroupIDs": [
            grp_id
        ]
    })
    headers = {"Content-Type": "application/json", "X-Auth-Token": token}
    response = requests.post(repo_url, headers=headers, data=repo_payload, verify=False)
    repo_payload_json = json.loads(repo_payload)
    name = repo_payload_json['Name']
    if response.status_code == 201:
        print(f'Created repository \'{name}\'')
    else:
        raise Exception(response.text)
        
token = get_auth_token()
catalog_id = get_catalog_id()    
grp_id = get_group_id()
create_repo()