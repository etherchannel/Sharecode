#this script can be used to discover idracs to be managed by openmanage enterprise
#written by rob.smith1@dell.com

#examples:
#py.exe .\ome_set_discovery_group_create.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -n "my stuff" -r 192.168.1.128 -d root -e calvin
#py.exe .\ome_set_discovery_group_create.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -n "my stuff" -r 192.168.1.128-192.168.1.138 -d root -e calvin

#import python modules
import requests, warnings, argparse

#supress warnings
warnings.filterwarnings("ignore")

#define arguments and help messages
parser = argparse.ArgumentParser(description='discover systems to be managed by openmange enterprise')
parser.add_argument('-i', help='openmanage enterprise ip address', required=True)
parser.add_argument('-u', help='openmanage enterprise username', required=True)
parser.add_argument('-p', help='openmanage enterprise password', required=True)
parser.add_argument('-n', help='description/name for discovery job', required=True)
parser.add_argument('-r', help='idrac ip/range', required=True)
parser.add_argument('-d', help='idrac username', required=True)
parser.add_argument('-e', help='idrac password', required=True)

#map parser to variable
args = vars(parser.parse_args())

#map arguments to variables
ome_ip = args["i"]
ome_user = args["u"]
ome_pass = args["p"]
idrac_name = args["n"]
idrac_range = args["r"]
idrac_user = args["d"]
idrac_pass = args["e"]


url = "https://%s/api/DiscoveryConfigService/DiscoveryConfigGroups" % (ome_ip)

payload = "{\"DiscoveryConfigGroupName\":\"%s\",\"DiscoveryConfigGroupDescription\":\"null\",\"DiscoveryConfigModels\":[{\"DiscoveryConfigId\":1,\"DiscoveryConfigDescription\":\"\",\"DiscoveryConfigStatus\":\"\",\"DiscoveryConfigTargets\":[{\"DiscoveryConfigTargetId\":0,\"NetworkAddressDetail\":\"%s\",\"AddressType\":30,\"Disabled\":false,\"Exclude\":false}],\"ConnectionProfileId\":0,\"ConnectionProfile\":\"{\\\"profileName\\\":\\\"\\\",\\\"profileDescription\\\":\\\"\\\",\\\"type\\\":\\\"DISCOVERY\\\",\\\"credentials\\\":[{\\\"id\\\":0,\\\"type\\\":\\\"WSMAN\\\",\\\"authType\\\":\\\"Basic\\\",\\\"modified\\\":false,\\\"credentials\\\":{\\\"username\\\":\\\"%s\\\",\\\"password\\\":\\\"%s\\\",\\\"caCheck\\\":false,\\\"cnCheck\\\":false,\\\"port\\\":443,\\\"retries\\\":3,\\\"timeout\\\":60,\\\"isHttp\\\":false,\\\"keepAlive\\\":false}}]}\",\"DeviceType\":[1000]}],\"Schedule\":{\"RunNow\":true,\"RunLater\":false,\"Cron\":\"startnow\",\"StartTime\":\"\",\"EndTime\":\"\"},\"CreateGroup\":true,\"TrapDestination\":true}" % (idrac_name, idrac_range, idrac_user, idrac_pass)

headers = {'Content-Type': 'application/json'}

response = requests.post(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))

#print(response.text)
#print(response.status_code)

if response.status_code == 201:
    print("Discovery group created.")
else:
    print(response.text)
    print(response.status_code)
