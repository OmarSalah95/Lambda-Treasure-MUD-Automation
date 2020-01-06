import requests
import json

# Load API key
key = open("api_key.txt", "r").read()

r = requests.get("https://lambda-treasure-hunt.herokuapp.com/api/adv/init/",
                 headers={'Authorization': f"Token {key}"})
data = r.json()
del data['players']
print(data)
