from api import url, key
import requests
import json


class Player:
    def __init__(self):
        data = self._get_status()
        current_map = self._read_map()

        self.name = data['name']
        self.cooldown = data['cooldown']
        self.encumbrance = data['encumbrance']
        self.strength = data['strength']
        self.speed = data['speed']
        self.gold = data['gold']
        self.bodywear = data['bodywear']
        self.footwear = data['footwear']
        self.inventory = []
        self.status = []
        self.errors = []
        self.messages = []
        self.map = current_map
        self.current_room = current_map['0']

    def _get_status(self):
        r = requests.post(f"{url}/api/adv/status/",
                          headers={'Authorization': f"Token {key}", "Content-Type": "application/json"})
        return r.json()

    def _read_map(self):
        with open('map.txt') as map_file:
            data = json.load(map_file)
            return data

    def check_room(self):
        r = requests.get(f"{url}/api/adv/init/",
                         headers={'Authorization': f"Token {key}"})
        data = r.json()
        del data['players']
        return data

    def check_self(self):
        data = self._get_status()
        self.name = data['name']
        self.cooldown = data['cooldown']
        self.encumbrance = data['encumbrance']
        self.strength = data['strength']
        self.speed = data['speed']
        self.gold = data['gold']
        self.bodywear = data['bodywear']
        self.footwear = data['footwear']
        self.inventory = data['inventory']
        self.status = data['status']
        self.errors = data['errors']
        self.messages = data['messages']

    def travel(self, direction):
        next_room = self.currentRoom.get_room_in_direction(direction)
        if next_room is not None:
            self.current_room = next_room
        else:
            print("You cannot move in that direction.")
