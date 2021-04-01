#examples:
#py.exe .\ome_set_discovery_group_delete.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -g 46

import requests
import json
import warnings
import argparse

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='discover systems to be managed by openmange enterprise')
parser.add_argument('-i', help='openmanage enterprise ip address', required=True)
parser.add_argument('-u', help='openmanage enterprise username', required=True)
parser.add_argument('-p', help='openmanage enterprise password', required=True)
parser.add_argument('-g', help='discovery range group id', required=True)

#map parser to variable
args = vars(parser.parse_args())

#map arguments to variables
ome_ip = args["i"]
ome_user = args["u"]
ome_pass = args["p"]
grp_id = args["g"]


url = "https://192.168.1.142/api/DiscoveryConfigService/Actions/DiscoveryConfigService.RemoveDiscoveryGroup"

payload = json.dumps({"DiscoveryGroupIds":['%s']}) % (grp_id)
headers = {'Content-Type': 'application/json'}

response = requests.post(url, headers=headers, data=payload, verify=False, auth=('admin', 'P@ssw0rd1'))
if response.status_code == 204:
    print("Discovery group deleted.")
else:
    print("Discovery group not deleted (verify that a valid group id was provided and that the discovery job is not currently running).")
