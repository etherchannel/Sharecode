import requests, json, warnings, re, argparse

#supress warnings
warnings.filterwarnings("ignore")

#open json file and save contents as variable called data
with open('clusterInventory_corrected.json') as file:
  data = json.load(file)
clusters = data["clusters"]

def main():
    global GroupName
    for a in clusters:
        for b in a.items():
            print("".ljust(100, '-'))
            GroupName = b[0]
            print("GROUP \"" + b[0] + "\" will be created if not already present.") #print clusters.[*].[0] <-key
            headers = {'content-type': 'application/json'}
            url = "https://192.168.1.141/api/GroupService/Actions/GroupService.CreateGroup"
            #payload = "{\"GroupModel\":{\"Id\":0,\"Name\":\"%s\",\"Description\":\"\",\"GlobalStatus\":0,\"DefinitionId\":0,\"MembershipTypeId\":12,\"ParentId\":1021}}" % (b[0]) #hard coded parent group id
            payload = json.dumps({"GroupModel":{"Id":0,"Name":"%s","Description":"","GlobalStatus":0,"DefinitionId":0,"MembershipTypeId":12,"ParentId":1021}}) % (b[0]) #hard coded parent group id "ParentId"
            response = requests.post(url, verify=False, headers=headers, data=payload, auth=('admin', 'P@ssw0rd'))
            status_code = response.status_code
            if status_code == 200:
                GroupId = response.text
            else:
                print("GROUP \"" + GroupName + "\" is already present.")
                get_group_id()
                GroupId = GId
            for c in b[1].items():
                for d in c[1]:
                    print("HOST \"" + d + "\" will be added to group if exists in OME and not already a group member.") #print each hostname
                    DeviceName1 = d
                    url2 = "https://192.168.1.141/api/DeviceService/Devices"
                    response = requests.get(url2, verify=False, auth=('admin', 'P@ssw0rd'))
                    value = response.json()['value']
                    for e in value:
                        if e["Type"] == 1000:
                            DeviceName2 = e["DeviceName"]
                            if DeviceName1 == DeviceName2:
                                DeviceID = e["Id"]
                                url3 = "https://192.168.1.141/api/GroupService/Actions/GroupService.AddMemberDevices"
                                payload = "{ \"GroupId\": %s, \"MemberDeviceIds\" : [%s]}" % (GroupId, DeviceID)
                                #payload = json.dumps({"GroupId": "%s","MemberDeviceIds": "[%s]"}) % (GroupId, DeviceID)
                                headers = {'Content-Type': 'application/json'}
                                response = requests.post(url3, verify=False, headers=headers, data=payload, auth=('admin', 'P@ssw0rd'))
                                #print(payload)
                                #print(response.status_code)
                                #print(response.content)
                                if response.status_code == 204:
                                    print("HOST \"" + d + "\" was added to group " + GroupName)
                                elif response.status_code != 200:
                                    print("HOST \"" + d + "\" is already a member of group.")

#translate group name to id
def get_group_id():
    global GId
    url4 = "https://192.168.1.141/api/GroupService/Groups"
    response = requests.get(url4, verify=False, auth=('admin', 'P@ssw0rd'))
    parsed = response.json()
    value = parsed['value']
    for a in value:
        if a['Name'] == GroupName:
            GId = a['Id']

if __name__ == '__main__':
  main()
