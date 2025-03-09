#This script is used to run racadm commands against systems managed by openmanage enterprise.
#example 1 runs racadm command against all systems managed by ome: python ome_42_remote_cli.py -i 172.26.38.195 -u admin -p P@ssw0rd -c 'getsysinfo'
#example 2 runs racadm command against systems in a group called 'All Devices': ome_42_remote_cli.py -i ome-lmc.ose.adc.delllabs.net -u oseadmin -p OSETe@mR0ckz! -c 'getsysinfo' -g 'All Devices'

import requests, warnings, json, argparse, time

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

def get_group_id(ome_target) -> int:
    url = f"https://{ome_ip}/api/GroupService/Groups"
    headers = {
        "Content-Type": "application/json", 
        "X-Auth-Token": token
        }
    response = requests.get(url, headers=headers, verify=False)
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
    headers_cli = {
        "Content-Type": "application/json", 
        "X-Auth-Token": token
        }
    response_cli = requests.get(url_cli, headers=headers_cli, verify=False)
    response_cli_json = response_cli.json()
    count = 0
    for each in response_cli_json['value']:
        count += 1
        Id = each['Id'] 
        Name = each.get('Name') or each.get('DeviceName')
        if command != None:
            url_jobs = f"https://{ome_ip}/api/JobService/Jobs"
            payload_jobs = json.dumps({"JobName":"Remote Command Line","JobDescription":"RACADM CLI","Schedule":"startnow","State":"enabled","Targets":[{"Id":int(Id),"Data":"","TargetType":{"Id":1000,"Name":"DEVICE"}}],"Params":[{"Key":"CommandTimeout","Value":"60"},{"Key":"operationName","Value":"REMOTE_RACADM_EXEC"},{"Key":"Command","Value":command}],"JobType":{"Name":"DeviceAction_Task","Internal":False}})
            response_jobs = requests.post(url_jobs, headers=headers_cli, data=payload_jobs, verify=False, auth=(ome_username, ome_password))
            response_jobs_json = response_jobs.json()
            job_id = response_jobs_json["Id"]
            if response_jobs.status_code == 201:
                print(f'RACADM command \'{command}\' sent for {Name}')
                print(f'Pausing for 30 seconds to allow job to complete')
                time.sleep(30)
                print(f'Getting command output for {Name}')
                print("=" * 80)
                get_output(ome_ip, job_id)
            else:
                print(f'RACADM command \'{command}\' failed for {Name}')
        else:
            print ('Append script execution with -c <RACADM command>')
            exit()
    print(f'The command was executed against {count} systems')

def get_output(ome_ip, job_id):
    headers_output = {
        "Content-Type": "application/json", 
        "X-Auth-Token": token
        }
    url_output = f'https://{ome_ip}/api/JobService/Jobs({job_id})/ExecutionHistories'
    response_output = requests.get(url_output, headers=headers_output, verify=False)
    if response_output.status_code == 200:
        value_output = response_output.json()["value"]
        if value_output:  # Check if the list is not empty
            url_append = value_output[0]["ExecutionHistoryDetails@odata.navigationLink"]
            url_execution = f'https://{ome_ip}/{url_append}'
            response_execution = requests.get(url_execution, headers=headers_output, verify=False, auth=(ome_username, ome_password))
            print(response_execution.json())
            # progress = 0  # initial value
            # while progress != 100:
            # # check the value (e.g. read from a file, API, etc.)
            #     progress = int(response_execution.json()["value"][0]["Progress"])
            #     print("Current progress:", progress)
            #     time.sleep(1)  # wait for 1 second before checking again
            command_output = response_execution.json()["value"][0]["Value"]
            print(command_output)        
        else:
            print("No execution history found")
    else:
        raise Exception("Failed to retrieve job status")

token = get_auth_token()
ome_grp_id = get_group_id(ome_target) if ome_target else None
url_cli = cli_url(ome_grp_id)
run_cli(url_cli)