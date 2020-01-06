import requests
import json

from player import Player
from api import url, key

player = Player()


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
