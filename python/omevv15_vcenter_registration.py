#This script will register a vcenter server in the openmanage enterprise vcenter plugin.

import requests, json

requests.packages.urllib3.disable_warnings()

ome_ip = ''       #use fqdn
ome_username = ''
ome_password = ''
vcenter_ip = ''  #use fqdn
vcenter_username = ''
vcenter_password = ''

def register_vcenter() -> None:
    url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles"
    payload = json.dumps({
    "consoleAddress": vcenter_ip,
    "description": "",
    "credential": {
        "username": vcenter_username,
        "domain": "",
        "password": vcenter_password
    },
    "extensions": [
        "WEBCLIENT",
        "PHA",
        "VLCM"
    ],
    "disableCNcheck": True
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload, verify=False, auth=(ome_username, ome_password))
    print(f"Attempting to register vCenter {vcenter_ip}")
    if response.status_code == 201:
        print(f"Successfully registered vCenter")
    else:
        raise Exception(response.text)

register_vcenter()
