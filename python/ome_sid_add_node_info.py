# looks up servers that have announced themselves to ome, filters out all but those that have NOT been discovered, passes credentials needed for discovery
# exmple) python.exe .\ome_sid_add_node_info.py -i <OME IP> -u <OME USER> -p <OME PASSWORD> -r <IDRAC USER> -c <IDRAC PASSWORD>
# exmple) python.exe .\ome_sid_add_node_info.py -i 192.168.1.141 -u admin -p P@ssw0rd1 -r root -c calvin
#import python modules
import requests, json, warnings, re, argparse

#supress warnings
warnings.filterwarnings("ignore")

#define arguments and help messages
parser = argparse.ArgumentParser(description='Push OME Server Initiated Discovery Information')
parser.add_argument('-i', help='OpenManage Enterprise IP Address', required=True)
parser.add_argument('-u', help='OpenManage Enterprise Username', required=True)
parser.add_argument('-p', help='OpenManage Enterprise Password', required=True)
parser.add_argument('-s', help='Target System Service Tag', required=False)
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

#uri variables
base_uri = "https://%s/api" % (ome_ip)
signal_nodes = "/DiscoveryConfigService/SignaledNodes"
node_info = "/DiscoveryConfigService/Actions/DiscoveryConfigService.UploadNodeInfo"

#open json file and save contents as variable called data
def load_data_file():
    global value
    with open('sid.json') as file:
      data = json.load(file)
    value = data['value']
    parse_node_data()

#api call to get info and save contents as variable called data
def load_data_api():
    global value
    url = base_uri+signal_nodes
    payload = {}
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))
    response_json = response.json()
    value = response_json['value']
    parse_node_data()

#read service tags of systems when status == annouced
def parse_node_data():
    global ServiceTag
    for a in value:
        if a['Status'] == 1:
        #if a['Status'] == 2:
        #if a['Status'] == 6:
            ServiceTag = a['ServiceTag']
            print(ServiceTag)
            pass_in_creds()

#pass service tags and credentials to ome
def pass_in_creds():
    url = base_uri+node_info
    payload = json.dumps({"AnnouncedTarget": [{"ServiceTag": ServiceTag, "UserName": idrac_user, "Password": idrac_pass, "CredentialType": "WSMAN"}]})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data = payload, verify=False, auth=(ome_user, ome_pass))
    if response.text == "0":
        print('Node info was sucessfully added for', ServiceTag)
    else:
        print('Node info failed to be added for', ServiceTag)

#init the script
if __name__ == '__main__':
  #load_data_file()
  load_data_api()
