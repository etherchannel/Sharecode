#purpose: return the service tages of servers in specified group or list of groups w/id
#createdby: rob.smith1@dell.com; mindingmyowndata@gmail.com
#example1: py.exe .\ome_get_device_group_serials.py -i 192.168.1.142 -u admin -p P@ssw0rd1
#example3: python.exe .\ome_get_device_group_serials.py -i 192.168.1.142 -u admin -p P@ssw0rd1 | grep admin
#example2: py.exe .\ome_get_device_group_serials.py -i 192.168.1.142 -u admin -p P@ssw0rd1 -g 10095

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
            #print(str1.ljust(125, '-'))
            #print(str5.ljust(25, ' ')+str3+devices_uri)
            for b in a.items():
                if b[0] == "DeviceServiceTag":
                    str4 = "%s" % b[1]
                    #print(str2.ljust(25, ' ')+str3+str4)
                    print(str4)
                elif b[0] == "InventoryDetails@odata.navigationLink":
                    inventory_details_url = "https://%s%s" % (ome_ip,b[1])
                    #print(str5.ljust(25, ' ')+str3+inventory_details_url)
                    #get_idrac_mac()
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
