#script was written and tested using python 3.9.5 targeting a dell poweredge m620 running idrac firmware 2.65.65.65
#script pulls service tag from target idrac, calls second script to push discovery (s.i.d.), passes tag as argument for second script
#second script, ome_server_initiated_discovery_node_info.py, must reside in the same directory as this script.
#intented for lab use only.
#written by rob_smith1@dell.com, mindingmyowndata@gmail.com.
#example) py.exe .\idrac_call_other_script.py -ii 192.168.1.126 -iu root -ip calvin -oi 192.168.1.141 -ou admin -op P@ssw0rd


import requests, json, sys, re, time, warnings, argparse, subprocess
warnings.filterwarnings("ignore")

parser=argparse.ArgumentParser(description="")
parser.add_argument('-ii',help='iDRAC IP address', required=True)
parser.add_argument('-iu', help='iDRAC username', required=True)
parser.add_argument('-ip', help='iDRAC password', required=True)
parser.add_argument('-oi',help='OME IP address', required=True)
parser.add_argument('-ou', help='OME username', required=True)
parser.add_argument('-op', help='OME password', required=True)

args=vars(parser.parse_args())

idrac_ip= args["ii"]
idrac_user= args["iu"]
idrac_pass= args["ip"]
ome_ip= args["oi"]
ome_user= args["ou"]
ome_pass= args["op"]

def serial():
    global serial
    url = 'https://%s/redfish/v1/Chassis/System.Embedded.1' % (idrac_ip)
    response = requests.get(url,verify=False,auth=(idrac_user, idrac_pass))
    data = response.json()
    serial = data['SKU']
    print('The service tag for this system is '+serial+'.')

def callotherscript():
    otherscript = 'py.exe .\ome_server_initiated_discovery_node_info.py -i %s -u %s -p %s -s %s -r root -c calvin' % (ome_ip, ome_user, ome_pass, serial)
    print('This is the call being made to execute the second script: '+otherscript)
    subprocess.run(otherscript)

if __name__ == "__main__":
    serial()
    callotherscript()
