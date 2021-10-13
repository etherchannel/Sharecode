#   This script lists auto deploy job details from openmanage enterprise.
#   Example) py .\ome_auto_deploy_list.py -i 192.168.1.142 -u admin -p P@ssw0rd1
#   Written using ome 3.6.1 and python 3.9.5 w/requests module (pip install requests)
#   Written by rob_smith1@dell.com, mindingmyowndata@gmail.com.
#   For lab use only.

#import python modules
import requests, warnings, argparse, json, sys

#supress warnings
warnings.filterwarnings('ignore')

#define arguments and help messages
parser = argparse.ArgumentParser(description='List OME Auto Deploy Jobs')
parser.add_argument('-i', help='OpenManage Enterprise IP Address', required=True)
parser.add_argument('-u', help='OpenManage Enterprise Username', required=True)
parser.add_argument('-p', help='OpenManage Enterprise Password', required=True)

#map parser to variable
args = vars(parser.parse_args())

#map arguments to variables
ome_ip = args["i"]
ome_user = args["u"]
ome_pass = args["p"]

#query ome for auto deploy job
url = "https://%s/api/AutoDeployService/Targets" % (ome_ip)
payload = {}
headers = {'Content-Type': 'application/json'}
response = requests.get(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))
data = response.json()
data_pretty = json.dumps(data, indent=2)
print(" Status Code: ", response.status_code, "\n", "Returned Data:\n", data_pretty)
