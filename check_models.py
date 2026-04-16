import requests
try:
    resp = requests.get("http://192.168.1.7:1234/v1/models")
    print(resp.json())
except Exception as e:
    print(e)
