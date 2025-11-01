#This script will create a server discovery job in openmanage enterprise to onboard a single or range of idracs.

import requests, json

requests.packages.urllib3.disable_warnings()

ome_ip = '172.26.38.195'                 #openmanage enterprise ip or fqdn
ome_username = 'admin'
ome_password = 'P@ssw0rd'
drac_ip_range = "192.168.1.126-192.168.1.127"           #ip address or ip range of idracs to be discovered
drac_username = "root"                                  #username of idracs to be discovered
drac_password = "calvin"                                #password of idracs to be discovered

def get_auth_token() -> str:
    """Get an authentication token from OpenManage Enterprise."""
    auth_url = f"https://{ome_ip}/api/SessionService/Sessions"
    auth_payload = {"UserName": ome_username, "Password": ome_password, "SessionType": "API"}
    auth_headers = {"Content-Type": "application/json"}
    response = requests.post(auth_url, headers=auth_headers, data=json.dumps(auth_payload), verify=False, auth=(ome_username, ome_password))
    if response.status_code == 201:
        print("Successfully authenticated to OpenManage Enterprise")
        return response.headers["X-Auth-Token"]        
    raise Exception(f"Authentication failed with status code: {response.status_code}")

def create_discovery_group() -> None:
    discovery_url = f"https://{ome_ip}/api/DiscoveryConfigService/DiscoveryConfigGroups"
    discovery_payload = "{\"DiscoveryConfigGroupName\":\"API Created Discovery Job\",\"DiscoveryConfigGroupDescription\":\"null\",\"DiscoveryConfigModels\":[{\"DiscoveryConfigId\":1,\"DiscoveryConfigDescription\":\"\",\"DiscoveryConfigStatus\":\"\",\"DiscoveryConfigTargets\":[{\"DiscoveryConfigTargetId\":0,\"NetworkAddressDetail\":\"%s\",\"AddressType\":30,\"Disabled\":false,\"Exclude\":false}],\"ConnectionProfileId\":0,\"ConnectionProfile\":\"{\\\"profileName\\\":\\\"\\\",\\\"profileDescription\\\":\\\"\\\",\\\"type\\\":\\\"DISCOVERY\\\",\\\"credentials\\\":[{\\\"id\\\":0,\\\"type\\\":\\\"WSMAN\\\",\\\"authType\\\":\\\"Basic\\\",\\\"modified\\\":false,\\\"credentials\\\":{\\\"username\\\":\\\"%s\\\",\\\"password\\\":\\\"%s\\\",\\\"caCheck\\\":false,\\\"cnCheck\\\":false,\\\"port\\\":443,\\\"retries\\\":3,\\\"timeout\\\":60,\\\"isHttp\\\":false,\\\"keepAlive\\\":false}}]}\",\"DeviceType\":[1000]}],\"Schedule\":{\"RunNow\":true,\"RunLater\":false,\"Cron\":\"startnow\",\"StartTime\":\"\",\"EndTime\":\"\"},\"CreateGroup\":true,\"TrapDestination\":true}" % (drac_ip_range, drac_username, drac_password)
    headers = {"Content-Type": "application/json", "X-Auth-Token": token}
    response = requests.post(discovery_url, headers=headers, data=discovery_payload, verify=False)
    if response.status_code == 201:
        print(f"Discovery initiated successfully for ip/range {drac_ip_range}")
    else:
        raise Exception(f"Discovery job failed to initiate with status code: {response.status_code}")

token = get_auth_token()
create_discovery_group()