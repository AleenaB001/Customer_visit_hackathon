import requests
import json
from requests.auth import HTTPBasicAuth
from config import *

url = f"{SN_INSTANCE}/api/now/table/kb_knowledge"

params = {
    "sysparm_query": "sys_id=42475b7497bd4b10a356f84de053af08",
    "sysparm_display_value": "true"
}

response = requests.get(
    url,
    auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
    params=params
)

record = response.json()["result"][0]

for key, value in record.items():
    if isinstance(value, str) and len(value) > 0:
        print("=" * 60)
        print(key)
        print(value)