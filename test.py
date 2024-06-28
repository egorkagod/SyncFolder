import os
import json
import requests

url = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'OAuth y0_AgAAAABxcWZdAADLWwAAAAEIzoS5AAAEeJnGQWhA9IaoyQLGIrWboGrzqQ'
}

params = {
    'path': 'disk:/Applications/Yandex Polygon/SyncFolder/',
    'fields': 'name, _embedded.items.path,_embedded.items.name, _embedded.items.type'
}

response = requests.get(url, headers=headers, params=params)
print(response.status_code)
print(json.dumps(response.json(), indent=4))
