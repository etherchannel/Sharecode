#   This script can be used to provide inforamtion required for ome server initiated discovery feature.
#   Example) py.exe .\ome_server_initiated_discovery_node_info.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -s UUU6FC9 -r root -c calvin 
#   Written using ome 3.6.1 and python 3.9.5.
#   Written by rob_smith1@dell.com, mindingmyowndata@gmail.com.
#   For lab use only.

#import python modules
import requests, warnings, argparse, json, sys

#supress warnings
warnings.filterwarnings("ignore")

#define arguments and help messages
parser = argparse.ArgumentParser(description='Push OME Server Initiated Discovery Information')
parser.add_argument('-i', help='OpenManage Enterprise IP Address', required=True)
parser.add_argument('-u', help='OpenManage Enterprise Username', required=True)
parser.add_argument('-p', help='OpenManage Enterprise Password', required=True)
parser.add_argument('-s', help='Target System Service Tag', required=True)
parser.add_argument('-r', help='Target System User Name', required=True)
parser.add_argument('-c', help='Target System Password', required=True)

#map parser to variable
args = vars(parser.parse_args())

#map arguments to variables
ome_ip = args["i"]
ome_user = args["u"]
ome_pass = args["p"]
svc_tag = args["s"]
idrac_user = args["r"]
idrac_pass = args["c"]

#push node info to ome
url = "https://%s/api/DiscoveryConfigService/Actions/DiscoveryConfigService.UploadNodeInfo" % (ome_ip)
payload = json.dumps({"AnnouncedTarget": [{"ServiceTag": svc_tag, "UserName": idrac_user, "Password": idrac_pass, "CredentialType": "WSMAN"}]})
headers = {'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))
if response.text == "0":
    print('Node info was sucessfully added for ' + svc_tag + ".")
else:
    print('Node info failed to be added for ' + svc_tag + ".")
