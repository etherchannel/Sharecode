import requests
import json
from datetime import date, datetime

requests.packages.urllib3.disable_warnings()

ome_ip = 'o_ip'
ome_username = 'o_user'
ome_password = 'o_pass'
catalog_version = "24.07.10" #https://www.dell.com/support/kbdoc/en-us/000225254/firmware-catalog-for-dell-s-vsan-ready-nodes-with-esxi-8-x-branch-images

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
        print("Successfully authenticated to OpenManage Enterprise")
        return response.headers["X-Auth-Token"]        
    raise Exception(f"Authentication failed with status code: {response.status_code}")

def get_catalog_id() -> str:
    catalog_url = f"https://{ome_ip}/api/UpdateManagementService/Catalogs"
    headers = {
        "Content-Type": "application/json", 
        "X-Auth-Token": token
        }
    response = requests.get(catalog_url, headers=headers, verify=False)
    response_json = response.json()
    response_pretty = json.dumps(response_json, indent=4)

    if response.status_code == 200:
        print('Retrieving catalog data')
    else:
        raise Exception(f"Catalog retrieval failed with status code: {response.status_code}")
    
    vsan_catalog_items = []
    for catalog in response_json['value']:
        if catalog['Key'].startswith("Index Catalog"):
            for item in catalog['Value']:
                if item['Key'] == "vSAN Catalog for Enterprise Servers":
                    for vsan_item in item['Value']:
                        if vsan_item['Key'] == catalog_version:  
                            vsan_catalog_items.append(vsan_item)
                            vsan_catalog_id = vsan_item['Id']   
    return vsan_catalog_id

def get_group_id() -> str:
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
        raise Exception(f"Unable to retrieve group data; failed with status code: {response.status_code}")
    
    for each in response_json['value']:
        name = each['Name']
        if name == 'All Devices':
            grp_id = each['Id']
            print(f'Captured \'All Devices\' group Id of {grp_id}')
            return grp_id

def create_repo() -> str:
    repo_url = f"https://{ome_ip}/api/UpdateManagementService/Repositories"
    now = datetime.now()
    f_now = now.strftime("%d%m%y %H%M%S")
    repo_payload = json.dumps({
        "BaseCatalogID": f"{catalog_id}",
        "BaseCatalogName": f"Index Catalog-{catalog_version}",
        "Name": f"API Created Repository {f_now}",
        "DeviceSelectionType": "groups",
        "BaselineName": f"API Created Repository {f_now}",
        "IsBaseline": True,
        "GroupIDs": [
            grp_id
        ]
    })
    headers = {"Content-Type": "application/json", "X-Auth-Token": token}
    response = requests.post(repo_url, headers=headers, data=repo_payload, verify=False)
    if response.status_code == 201:
        print(f'Successfully created vSAN repository from catalog {catalog_version}')
    else:
        print(response.text)
        raise Exception(f"Repository failed with status code: {response.status_code}")
        
token = get_auth_token()
catalog_id = get_catalog_id()    
grp_id = get_group_id()
create_repo()