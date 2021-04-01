#purpose: return ip/mac address info of servers in specified group or list of groups w/id
#createdby: rob.smith1@dell.com; mindingmyowndata@gmail.com
#example1: py.exe .\ome_get_device_group_details.py -i 192.168.1.142 -u admin -p P@ssw0rd1
#example2: py.exe .\ome_get_device_group_details.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -g 10095
#example3: python.exe .\ome_get_device_group_details.py -i 192.168.1.142 -u admin -p P@ssw0rd1 | grep admin
#notes: systems discovered via non-idrac ip may return unexpected results

import requests, json, warnings, re, argparse

#supress warnings
warnings.filterwarnings("ignore")

#define required arguments as well as help/usage messages
parser = argparse.ArgumentParser(description='List device groups along with associated IDs or export IP/NIC info of member servers')
parser.add_argument('-i', help='OME IP', required=True)
parser.add_argument('-u', help='OME User', required=True)
parser.add_argument('-p', help='OME Password', required=True)
parser.add_argument('-g', help='OME Server Group ID', required=False)

args = vars(parser.parse_args())

#map user provided agruments to variables
ome_ip = args["i"]
ome_user = args["u"]
ome_pass = args["p"]
ome_grp = args["g"]

#loop through network detail and capture relavant data
def get_network_interface_details():
    headers = {'content-type': 'application/json'}
    response = requests.get(network_interfaces_url, verify=False, headers=headers, auth=(ome_user, ome_pass))
    response_json = response.json()
    value = response_json['InventoryInfo']
    for a in value:
        for b in a.items():
            if b[0] == "NicId":
                str1 = "NIC FQDD"
                str2 = "--> "
                str3 = "%s" % b[1]
                print(str1.ljust(25, ' ')+str2+str3)
            elif b[0] == "Ports":
                for c in b[1]:
                    for d in c.items():
                        if d[0] == "PortId":
                            str4 = " Port"
                            str5 = "%s" % d[1]
                            print(str4.ljust(25, ' ')+str2+str5)
                        elif d[0] == "ProductName":
                            model = re.search('^.*(?=(\\-))', d[1]) #regex model to ignore extra info in field
                            str18 = "  Model"
                            str19 = "%s" % model.group()
                            print(str18.ljust(25, ' ')+str2+str19)
                        elif d[0] == "Partitions":
                            for e in d[1][0].items():
                                if e[0] == "Fqdd":
                                    str6 = "  Partition"
                                    str7 = "%s" % e[1]
                                    print(str6.ljust(25, ' ')+str2+str7)
                                elif e[0] == "CurrentMacAddress":
                                    str8 = "  Current MAC"
                                    str9 = "%s" % e[1]
                                    print(str8.ljust(25, ' ')+str2+str9)
                                elif e[0] == "PermanentMacAddress":
                                    str10 = "  Permanent MAC"
                                    str11 = "%s" % e[1]
                                    print(str10.ljust(25, ' ')+str2+str11)
                                elif e[0] == "PermanentIscsiMacAddress":
                                    str12 = "  Permanent ISCSI MAC"
                                    str13 = "%s" % e[1]
                                    print(str12.ljust(25, ' ')+str2+str13)
                                elif e[0] == "VirtualMacAddress":
                                    str14 = "  Virtual MAC"
                                    str15 = "%s" % e[1]
                                    print(str14.ljust(25, ' ')+str2+str15)
                                elif e[0] == "VirtualIscsiMacAddress":
                                    str16 = "  Virtual ISCSI MAC"
                                    str17 = "%s" % e[1]
                                    print(str16.ljust(25, ' ')+str2+str17)

#identify device network url to pass to interface_details function
def get_network_interfaces_url():
    global network_interfaces_url
    headers = {'content-type': 'application/json'}
    response = requests.get(inventory_details_url, verify=False, headers=headers, auth=(ome_user, ome_pass))
    response_json = response.json()
    value = response_json['value']
    for a in value:
        for b in a.items():
            if "\'serverNetworkInterfaces\'" in b[1]:
                network_interfaces_url = "https://%s%s" % (ome_ip,b[1])
                str1 = "Data Source"
                str2 = "--> "
                print(str1.ljust(25, ' ')+str2+network_interfaces_url)
                get_network_interface_details()

#capture idrac mac and ip
def get_idrac_mac():
    headers = {'content-type': 'application/json'}
    response = requests.get(inventory_details_url, verify=False, headers=headers, auth=(ome_user, ome_pass))
    response_json = response.json()
    value = response_json['value']
    for a in value:
        for b in a.items():
            if b[0] == "InventoryInfo":
                for c in b[1]:
                    for d in c.items():
                        if d[0] == "MacAddress":
                            mac = d[1]
                            MAC = mac.upper()
                        elif d[0] == "IpAddress":
                            ip = d[1]
                        elif d[0] == "EndPointAgents":
                            for e in d[1]:
                                for f in e.items():
                                    #print(f)
                                    if f[1] == "iDRAC":
                                        str1 = "iDRAC IP"
                                        str2 = "--> %s" % ip
                                        str3 = "iDRAC MAC"
                                        str4 = "--> %s" % MAC
                                        print(str1.ljust(25, ' ')+str2)
                                        print(str3.ljust(25, ' ')+str4)
                                        get_network_interfaces_url()

#capture service tag and the url for device specific inventory data
def get_inventory_url():
    global inventory_details_url
    headers = {'content-type': 'application/json'}
    base_uri = "https://%s" % (ome_ip)
    devices_uri = base_uri + "/api/GroupService/Groups(%s)/Devices" % (ome_grp)
    response = requests.get(devices_uri, verify=False, headers=headers, auth=(ome_user, ome_pass))
    response_json = response.json()
    value = response_json['value']
    count = response_json['@odata.count'] #capture number of systems included in group as variable
    if count != 0: #account for groups with no members
        for a in value:
            str1 = ""
            str2 = "System ID"
            str3 = "--> "
            str5 = "Data Source"
            str6 = "Device Name"
            print(str1.ljust(125, '-'))
            print(str5.ljust(25, ' ')+str3+devices_uri)
            for b in a.items():
                if b[0] == "DeviceServiceTag":
                    str4 = "%s" % b[1]
                    print(str2.ljust(25, ' ')+str3+str4)
                elif b[0] == "DeviceName":
                    str7 = "%s" % b[1]
                    print(str6.ljust(25, ' ')+str3+str7)
                elif b[0] == "InventoryDetails@odata.navigationLink":
                    inventory_details_url = "https://%s%s" % (ome_ip,b[1])
                    print(str5.ljust(25, ' ')+str3+inventory_details_url)
                    get_idrac_mac()
    else:
        print("Group Contains No Members")

#check that group id provided by user actually exists
def verify_grp_id():
    base_uri = "https://%s" % (ome_ip)
    groups_uri = base_uri + "/api/GroupService/Groups"
    headers = {'content-type': 'application/json'}
    response = requests.get(groups_uri, verify=False, headers=headers, auth=(ome_user, ome_pass))
    response_json = response.json()
    isPresent = False
    value = response_json['value']
    for a in value:
        for b in a.items():
            if b[0] == "Id":
                b1_str = str(b[1])
                if ome_grp == b1_str:
                    isPresent = True
                    break
    if isPresent == True:
        get_inventory_url()
    else:
        print("Group ID provided is not valid")

#list groups along with corresponding group id
def get_grp_id():
    base_uri = "https://%s" % (ome_ip) #variable for base api url
    groups_uri = base_uri + "/api/GroupService/Groups" #build full url
    headers = {'content-type': 'application/json'} #parameters needed to properly interface with api
    response = requests.get(groups_uri, verify=False, headers=headers, auth=(ome_user, ome_pass)) #use requests module to access rest api and save return data as variable
    response_json = response.json() #process returned data as json
    value = response_json['value'] #advance to relavent portion of returned data
    str0 = "Data Source --> "
    print(str0.ljust(40)+groups_uri) #show url where groups are retrieved from
    for a in value: #loop through objects
        for b in a.items(): #loop through key/value pairs within object
            if b[0] == "Id": #match specific key
                id = b[1] #once key matched assign key's value to variable
            elif b[0] == "Name":
                name = b[1]
            elif b[0] == "CreatedBy":
                createdby = b[1]
                str1 = "Group Name --> %s" % name #convert output stings to variables to aid in formating
                str2 = "Group ID --> %s" % id
                str3 = "CreatedBy --> %s" % createdby
                str4 = ""
                print(str4.ljust(100, '-')) #create line to visually segment returned records
                print(str1.ljust(40)+str2.ljust(20)+str3) #format spacing of returned data

#if group argument NOT passed in by user, call function to list group info otherwise call function to start capturing and displaying network details for group member servers
def main():
    if ome_grp == None:
        get_grp_id()
    else:
        verify_grp_id()

if __name__ == '__main__':
  main()
