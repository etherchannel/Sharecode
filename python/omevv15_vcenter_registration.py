import requests
import json

requests.packages.urllib3.disable_warnings()

ome_ip = 'demo-omevv-01-ome.ose.adc.delllabs.net'
ome_username = 'rob_smith1@ose.local'
ome_password = 'P@ssw0rd!23'
vcenter_ip = 'demo-omevv-01-vcsa.ose.adc.delllabs.net'
vcenter_username = "administrator@vsphere.local"
vcenter_password = "L@bT3@m>C0vid"

def register_vcenter() -> str:
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
        print(response.text)
        raise Exception(f"Registration failed with status code: {response.status_code}")

register_vcenter()
