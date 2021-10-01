#this script was written and tested using python 3.9.5 targeting a dell poweredge m620 running idrac firmware 2.65.65.65
#it is an example of how to pull a service tag from idrac and then pass it as an argument for a second script.
#ome_server_initiated_discovery_node_info.py resides in the same directory.
#it is intented for lab use only.
#written by rob_smith1@dell.com
#example) py.exe .\idrac_get_serial.py -ip 192.168.1.126 -u root -p calvin


import requests, json, sys, re, time, warnings, argparse, subprocess
#import ome_server_initiated_discovery_node_info
warnings.filterwarnings("ignore")

parser=argparse.ArgumentParser(description="")
parser.add_argument('-ip',help='iDRAC IP address', required=False)
parser.add_argument('-u', help='iDRAC username', required=False)
parser.add_argument('-p', help='iDRAC password', required=False)

args=vars(parser.parse_args())

idrac_ip= args["ip"]
idrac_username= args["u"]
idrac_password= args["p"]

def serial():
    global serial
    response = requests.get('https://%s/redfish/v1/Chassis/System.Embedded.1' % idrac_ip,verify=False,auth=(idrac_username, idrac_password))
    data = response.json()
    serial = data['SKU']
    print(serial)

def callotherscript():
    otherscript = 'py.exe .\ome_server_initiated_discovery_node_info.py -i 192.168.1.141 -u admin -p P@ssw0rd -s %s -r root -c calvin' % serial
    subprocess.run(otherscript)

if __name__ == "__main__":
    serial()
    callotherscript()
