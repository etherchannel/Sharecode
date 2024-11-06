import requests
import json

ome_ip = 'demo-omevv-01-ome.ose.adc.delllabs.net'
ome_username = 'rob_smith1@ose.local'
ome_password = 'P@ssw0rd!23'
vcenter_ip = 'demo-omevv-01-vcsa.ose.adc.delllabs.net'
vcenter_username = "administrator@vsphere.local"
vcenter_password = "L@bT3@m>C0vid"

url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles"

payload = json.dumps({
  "extensions": [
    "WEBCLIENT_PHA",
    "VLCM"
  ],
  "credential": {
    "username": vcenter_username,
    "password": vcenter_password
  },
  "consoleAddress": vcenter_ip,
  "description": "Registering VC"
})
headers = {'Content-Type': 'application/json'}

response = requests.post(url, headers=headers, data=payload, verify=False, auth=(vcenter_username, vcenter_password))

print(response.text)