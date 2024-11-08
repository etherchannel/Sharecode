#   This script creates auto deploy jobs in openmanage enterprise.
#   Arguments for ome ip, ome username, ome password, template id, and device service tag are required.
#   It is recommended to first create auto deploy job via gui then run ome_auto_deploy_list.py to identify value for template id.
#   For boot-to-iso functionality, the payload in request() can be modified with appropriate information.
#   Example) py.exe .\ome_auto_deploy_create.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -s UUU6FC9 -t 29
#   Written using ome 3.6.1 and python 3.9.5 w/requests module (pip install requests)
#   Written by rob_smith1@dell.com, mindingmyowndata@gmail.com.
#   For lab use only.

#import python modules
import warnings, argparse, json, sys, subprocess, pkg_resources
import requests

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

#validate provided service tag and create deployment id
def generate_auto_deployment_id():
    global autodeployid
    url = "https://%s/api/AutoDeployService/Actions/AutoDeployService.Verify" % (ome_ip)
    payload = json.dumps({"TemplateId":"%s","Identifiers":["%s"]}) % (template_id, svc_tag)
    headers = {'Content-Type': 'application/json'}
    print("Submitting Deployment ID request for " + svc_tag + " (prerequisite for Auto Deploy request)")
    response = requests.post(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))
    data = response.json()
    data_pretty = json.dumps(data, indent=2)
    print(" Returned Status Code: ", response.status_code, "\n", "Returned Data:\n", data_pretty)
    if response.status_code == 200:
        autodeployid = data['AutoDeployId']
        print("Deployment ID " + str(autodeployid) + " captured")
        #print("ID object type:", type(autodeployid))
    else:
        print("Deployment ID request for " + svc_tag + " failed")
        print("Troubleshooting Tip: Ensure sure that the supplied script argument data is valid, that an Auto Deploy job does not already exist for this system,", \
        "or that target system has not already been discovered by OME")
        sys.exit()

#create auto deploy job
def create_auto_deployment_job():
    url = "https://%s/api/AutoDeployService/AutoDeploy" % (ome_ip)
    payload = json.dumps({"AutoDeployId": autodeployid, "GroupId": None, "NetworkBootIsoModel": {"BootToNetwork": False, "ShareType": "", "IsoPath": "", \
    "ShareDetail": {"IpAddress": "", "ShareName": "", "User": "", "Password": ""}}, "Attributes": []})
    headers = {'Content-Type': 'application/json'}
    payload_json = json.loads(payload)
    payload_pretty = json.dumps(payload_json, indent=2)
    print("Submitting Auto Deploy job request for " + svc_tag)
    print("Payload data sent with request:\n", payload_pretty)
    response = requests.post(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))
    data = response.json()
    data_pretty = json.dumps(data, indent=2)
    print(" Returned Status Code: ", response.status_code, "\n", "Returned Data:\n", data_pretty)
    if response.text == '0':
        print("Auto Deploy request successful for " + svc_tag)
    else:
        print("Auto Deploy request failed for " + svc_tag)

#code execution
if __name__ == "__main__":
    generate_auto_deployment_id()
    create_auto_deployment_job()
