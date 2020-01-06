import requests
import json

from player import Player
from api import url, key

# key = open("api_key.txt", "r").read()
# url = "https://lambda-treasure-hunt.herokuapp.com"

r = requests.post(f"{url}/api/adv/status/",
                  headers={'Authorization': f"Token {key}", "Content-Type": "application/json"})
data = r.json()
# return data
player = Player(data)
print(player.name)
# Load API key


# def check_room():
#     r = requests.get(f"{url}/api/adv/init/",
#                      headers={'Authorization': f"Token {key}"})
#     data = r.json()
#     del data['players']
#     return data


# def read_map():
#     with open('map.txt') as map_file:
#         data = json.load(map_file)
#         print(f"current map: {data}")
#         return data


# def add_to_map(room):
#     map = read_map()
#     if room['room_id'] in map:
#         print("Room already in map")
#     else:
#         map = {}

#         # map[data['room_id']] = data

#         # with open('map.txt', 'w') as out:
#         #     json.dump(map, out)


# def move(direction):
#     pass
