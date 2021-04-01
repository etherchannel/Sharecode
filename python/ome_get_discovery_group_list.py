import requests
import warnings

warnings.filterwarnings("ignore")
url = "https://192.168.1.142/api/DiscoveryConfigService/Jobs"
payload={}
headers = {'Authorization': 'Basic YWRtaW46UEBzc3cwcmQx'}
response = requests.request("GET", url, headers=headers, data=payload, verify=False, auth=('admin', 'P@ssw0rd1'))
print(response.status_code)
print(response.text)
print(response.json())
print(response.context)
