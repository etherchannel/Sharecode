#This script will manage supported systems in the openmanage enterprise vcenter plugin.

import requests, json
from datetime import datetime

requests.packages.urllib3.disable_warnings()

ome_ip = '' #use fqdn
vcenter_ip = '' #use fqdn
vcenter_username = ''
vcenter_password = ''

def get_console_uuid() -> str:
    url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles"
    response = requests.get(url, verify=False, auth=(vcenter_username, vcenter_password))
    response_json = response.json()
    if response.status_code == 200:
        print('Getting console UUID data')
    else:
        raise Exception(response.text)
    for item in response_json: 
        uuid = None
        if item["consoleAddress"] == vcenter_ip: 
            uuid = item["uuid"] 
            print(f'Captured console UUID ({uuid})')
        else: 
            print("Ignoring UUID for out-of-scope console")
    if uuid == None:
        raise Exception(f"Unable to find {vcenter_ip} console UUID")
    else:
        return uuid

def compliance():
    url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles/{uuid}/Compliance"
    payload = {}
    headers = {
    'x_omivv-api-vcenter-identifier': uuid
    }
    response = requests.get(url, headers=headers, data=payload, verify=False, auth=(vcenter_username, vcenter_password))
    print('Getting Compliance data')
    if response.status_code == 200 and response.json() == []: 
        print("No systems are available to be managed") 
    elif response.status_code == 200 and response.json() != []:
        print("Systems available to be managed")
    else:
        raise Exception(response.text)
    return response.json()

def manage_hosts(hosts_data):
    for each in hosts_data:
        f_now = datetime.now().strftime("%d%m%y %H%M%S%f")
        id = each['hostid']
        hostname = each['hostName']
        if each['state'] == 'COMPLIANT' or each['state'] == 'NONCOMPLIANT' or each['state'] == 'Compliant' or each['state'] == 'Noncompliant':
            print(f'Getting host ({id})')
            headers = {
                'x_omivv-api-vcenter-identifier': uuid,
                'Content-Type': 'application/json'
            }
            payload = json.dumps({"jobName":f"Manage Job {f_now}","hostIDs":[id]})
            url = f"https://{ome_ip}/omevv/GatewayService/v1/Consoles/{uuid}/Hosts/Manage"
        response = requests.post(url, headers=headers, data=payload, verify=False, auth=(vcenter_username, vcenter_password))
        if response.status_code == 202:
            print(f"Scheduled manage job for host ({hostname})")
        else:
            print(f"Manage job failed for host {hostname} with error ({response.text})")

uuid = get_console_uuid()
hosts_data = compliance()
manage_hosts(hosts_data)