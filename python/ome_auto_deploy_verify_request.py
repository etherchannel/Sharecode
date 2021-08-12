#   This script creates auto deploy jobs in openmanage enterprise.
#   Arguments for ome ip, ome username, ome password, template id, and device service tag are required.
#   It is recommended to first create auto deploy job via gui then run ome_auto_deploy_list.py to identify value for template id.
#   For boot-to-iso functionality, the payload in request() can be modified with appropriate information.
#   Example) py.exe .\ome_auto_deploy_verify_request.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -s UUU6FC9 -t 29
#   Written using ome 3.6.1 and python 3.9.5.
#   Written by rob_smith1@dell.com, mindingmyowndata@gmail.com.
#   For lab use only.

#import python modules
import requests, warnings, argparse, json, sys

#supress warnings
warnings.filterwarnings("ignore")

#define arguments and help messages
parser = argparse.ArgumentParser(description='Create OME Auto Deploy Jobs')
parser.add_argument('-i', help='OpenManage Enterprise IP Address', required=True)
parser.add_argument('-u', help='OpenManage Enterprise Username', required=True)
parser.add_argument('-p', help='OpenManage Enterprise Password', required=True)
parser.add_argument('-s', help='Target System Service Tags', required=True)
parser.add_argument('-t', help='Service Profile/Template ID', required=True)

#map parser to variable
args = vars(parser.parse_args())

#map arguments to variables
ome_ip = args["i"]
ome_user = args["u"]
ome_pass = args["p"]
svc_tag = args["s"]
template_id = args["t"]

#validate provided service tag
def verify():
    global autodeployid
    url = "https://%s/api/AutoDeployService/Actions/AutoDeployService.Verify" % (ome_ip)
    payload = json.dumps({"TemplateId":"%s","Identifiers":["%s"]}) % (template_id, svc_tag)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))
    response_json = response.json()
    if response.status_code == 200:
        autodeployid = response_json['AutoDeployId']
        print("Service tag verification successful for " + svc_tag + ".")
    else:
        print("Service tag verification failed for " + svc_tag + ".  Ensure service tag syntax is valid and that an auto deploy job does not already exist.")
        sys.exit()

#create auto deploy job
def request():
    url = "https://%s/api/AutoDeployService/AutoDeploy" % (ome_ip)
    payload = json.dumps({"AutoDeployId": autodeployid, "GroupId": None, "NetworkBootIsoModel": {"BootToNetwork": False, "ShareType": "CIFS", "IsoPath": "abc.iso", "ShareDetail": {"IpAddress": "xx.xx.xx.xx", "ShareName": "10.22.33.22", "User": "asdf", "Password": "asdf"}}, "Attributes": []})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data = payload, verify=False, auth=('admin', 'P@ssw0rd1'))
    if response.text == '0':
        print("Auto Deploy job creation successful for " + svc_tag + ".")
    else:
        print("Auto Deploy job creation failed for " + svc_tag + ".")

#code execution
if __name__ == "__main__":
    verify()
    request()