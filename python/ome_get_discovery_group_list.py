#example1: py.exe .\ome_get_discovery_group_list.py -i 192.168.1.142 -u admin -p P@ssw0rd1

import requests
import warnings
import argparse

warnings.filterwarnings("ignore")

#supress warnings
warnings.filterwarnings("ignore")

#define arguments and help messages
parser = argparse.ArgumentParser(description='discover systems to be managed by openmange enterprise')
parser.add_argument('-i', help='openmanage enterprise ip address', required=True)
parser.add_argument('-u', help='openmanage enterprise username', required=True)
parser.add_argument('-p', help='openmanage enterprise password', required=True)

#map parser to variable
args = vars(parser.parse_args())

#map arguments to variables
ome_ip = args["i"]
ome_user = args["u"]
ome_pass = args["p"]

url = "https://192.168.1.142/api/DiscoveryConfigService/Jobs"
payload= {}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload, verify=False, auth=(ome_user, ome_pass))

print(response.status_code)
print(response.text)
