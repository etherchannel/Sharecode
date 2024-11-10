#This script is used to run racadm commands against systems managed by openmanage enterprise.
#example 1 runs racadm command against all systems managed by ome: ome_42_set_remote_cli.py -i ome-lmc.ose.adc.delllabs.net -u oseadmin -p OSETe@mR0ckz! -c 'getsysinfo'
#example 2 runs racadm command against systems in a group called 'All Devices': ome_42_set_remote_cli.py -i ome-lmc.ose.adc.delllabs.net -u oseadmin -p OSETe@mR0ckz! -c 'getsysinfo' -g 'All Devices'

import requests
import warnings
import json
import argparse

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='')
parser.add_argument('-c', help='RACADM Command', required=False)
parser.add_argument('-i', help='OpenManage Enterprise IP Address', required=False)
parser.add_argument('-u', help='OpenManage Enterprise Username', required=False)
parser.add_argument('-p', help='OpenManage Enterprise Password', required=False)
parser.add_argument('-r', help='Target System(s) IP or IP Range', required=False)
parser.add_argument('-g', help='Target Group', required=False)

args = vars(parser.parse_args())

command = args["c"]
ome_ip = args["i"]
ome_username = args["u"]
ome_password = args["p"]
ome_target = args["g"]
def get_group_id(ome_target) -> int:
    url = f"https://{ome_ip}/api/GroupService/Groups"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, verify=False, auth=(ome_username, ome_password))
    response_json = response.json()
    for each in response_json['value']:
        Name = each['Name']
        if Name == ome_target:
            ome_grp_id = each['Id']
            print(f'Found Id {ome_grp_id} for group \'{ome_target}\'')
            return ome_grp_id
    raise KeyError(f"Group '{ome_target}' not found")
        
def cli_url(ome_grp_id) -> str:
    if ome_target != None:
        print('Setting job scope to specified group')
        url_cli = f"https://{ome_ip}/api/GroupService/Groups({ome_grp_id})/Devices"
    else:
        print('Setting job scope to all managed iDRAC systems')
        url_cli = f"https://{ome_ip}/redfish/v1/Systems/Members?$top=8000"
    return url_cli

def run_cli(url_cli):
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url_cli, headers=headers, verify=False, auth=(ome_username, ome_password))
    response_json = response.json()
    count = 0
    for each in response_json['value']:
        count += 1
        Id = each['Id'] 
        Name = each.get('Name') or each.get('DeviceName')
        if command != None:
            url_jobs = f"https://{ome_ip}/api/JobService/Jobs"
            payload_jobs = json.dumps({"JobName":"Remote Command Line","JobDescription":"RACADM CLI","Schedule":"startnow","State":"enabled","Targets":[{"Id":int(Id),"Data":"","TargetType":{"Id":1000,"Name":"DEVICE"}}],"Params":[{"Key":"CommandTimeout","Value":"60"},{"Key":"operationName","Value":"REMOTE_RACADM_EXEC"},{"Key":"Command","Value":command}],"JobType":{"Name":"DeviceAction_Task","Internal":False}})
            response_jobs = requests.post(url_jobs, headers=headers, data=payload_jobs, verify=False, auth=(ome_username, ome_password))
            if response_jobs.status_code == 201:
                print(f'RACADM command \'{command}\' sucesssful for {Name}')
            else:
                print(f'RACADM command \'{command}\' failed for {Name}')
        else:
            print ('Append script execution with -c <RACADM command>')
            exit()
    print(f'Command executed for {count} systems')

ome_grp_id = get_group_id(ome_target) if ome_target else None
url_cli = cli_url(ome_grp_id)
run_cli(url_cli)