
import requests, json, sys, re, time, warnings, argparse
from datetime import datetime
warnings.filterwarnings("ignore")

parser=argparse.ArgumentParser(description="")
parser.add_argument('-ip',help='iDRAC IP address', required=False)
parser.add_argument('-u', help='iDRAC username', required=False)
parser.add_argument('-p', help='iDRAC password', required=False)

args=vars(parser.parse_args())

idrac_ip= args["ip"]
idrac_username= args["u"]
idrac_password= args["p"]

def power_consumed():
    response = requests.get('https://%s/redfish/v1/Chassis/System.Embedded.1/Power' % idrac_ip,verify=False,auth=(idrac_username, idrac_password))
    data = response.json()
    for A in data['PowerControl']:
        for B in A.items():
            if B[0] == 'PowerConsumedWatts':
                print(B[0], B[1])
def inlet_temp():
    response = requests.get('https://%s/redfish/v1/Chassis/System.Embedded.1/Thermal#/' % idrac_ip,verify=False,auth=(idrac_username, idrac_password))
    data = response.json()
    Z = data['Temperatures']
    for A in Z:
        for B in A.items():
            if B[0] == 'Name' and B[1] == 'System Board Inlet Temp':
                str = B[1].replace(" ", "")
                print(str,A['ReadingCelsius'])
def outlet_temp():
    response = requests.get('https://%s/redfish/v1/Chassis/System.Embedded.1/Thermal#/' % idrac_ip,verify=False,auth=(idrac_username, idrac_password))
    data = response.json()
    Z = data['Temperatures']
    for A in Z:
        for B in A.items():
            if B[0] == 'Name' and B[1] == 'System Board Exhaust Temp':
                str = B[1].replace(" ", "")
                print(str, A['ReadingCelsius'])
def current_time():
    time=datetime.now()
    print('TimeStamp',time)

if __name__ == "__main__":
    current_time()
    power_consumed()
    inlet_temp()
    outlet_temp()
