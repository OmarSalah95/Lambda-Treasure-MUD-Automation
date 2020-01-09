from api import url, key, opposite
import requests
import json
import time
import os
from miner import mine
from cpu import *


class Player:
    def __init__(self):
        data = self._get_status()
        time.sleep(data['cooldown'])

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
        self.abilities = []
        self.map = self._read_file('map.txt')
        self.graph = self._read_file('graph.txt')
        self.current_room = self.check_room()

    def _get_status(self):
        r = requests.post(f"{url}/api/adv/status/",
                          headers={'Authorization': f"Token {key}", "Content-Type": "application/json"})
        return r.json()

    def _read_file(self, filepath):
        with open(filepath) as f:
            data = json.load(f)
            return data

    def _write_file(self, filepath, data):
        with open(filepath, 'w') as outfile:
            json.dump(data, outfile)

    def check_room(self):
        r = requests.get(f"{url}/api/adv/init/",
                         headers={'Authorization': f"Token {key}"})
        data = r.json()
        if 'players' in data:
            del data['players']

        return data

    def check_self(self):
        data = self._get_status()
        print(data)
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
        self.abilities = data['abilities']
        
    def travel(self, direction, method="walk"):
        time.sleep(self.cooldown)
        curr_id = self.current_room['room_id']
        print(f"{method}ing {direction} from room {curr_id}...")

        if direction not in self.graph[str(curr_id)]:
            print("Error! Not a valid direction from the current room")
        else:
            json = {"direction": direction}
            if self.graph[str(curr_id)][direction] != "?":
                json['next_room_id'] = str(self.graph[str(curr_id)][direction])
            r = requests.post(f"{url}/api/adv/move/", headers={
                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json)
            next_room = r.json()
            if 'players' in next_room:
                del next_room['players']
            next_id = next_room['room_id']

            # add to graph and map, in addition to making graph connections
            if str(next_id) not in self.graph:
                self.graph[str(next_id)] = {
                    e: '?' for e in next_room['exits']}

            # make graph connections and update graph
            self.graph[str(curr_id)][direction] = next_id
            self.graph[str(next_id)][opposite[direction]] = curr_id
            self._write_file('graph.txt', self.graph)

            # update map with room info
            self.map[next_id] = next_room
            self._write_file('map.txt', self.map)

            # change current room and update cooldown
            self.current_room = next_room
            self.cooldown = self.current_room['cooldown']
            print(f"Now the player is in {self.current_room['room_id']}\n")
            if len(self.graph) < 500:
                print(
                    f"Total number of rooms explored so far: {len(self.graph)}\n")

    def get_coin(self):
        time.sleep(self.cooldown)
        data = mine()
        self.cooldown = data['cooldown']
        if len(data['errors']) > 0:
            self.get_coin()
        

    def pick_up_loot(self, item):
        time.sleep(self.cooldown)
        json = {"name": item}
        req = requests.post(f"{url}/api/adv/take/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
        time.sleep(req['cooldown'])
        self.check_self()

    def drop_loot(self, item):
        time.sleep(self.cooldown)
        json = {"name": item}
        req = requests.post(f"{url}/api/adv/drop/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
        time.sleep(req['cooldown'])
        self.check_self()

    def buy_name(self, name):
        time.sleep(self.cooldown)
        json = {"name": name}
        req = requests.post(f"{url}/api/adv/change_name/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
        print(req)

        time.sleep(req['cooldown'])

        json['confirm'] = "aye"
        r1_conf = requests.post(f"{url}/api/adv/change_name/", headers={
                                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
        print(r1_conf)
        time.sleep(r1_conf['cooldown'])
        self.check_self()

    def examine(self, item):
        time.sleep(self.cooldown)
        json = {"name": item}
        req = requests.post(f"{url}/api/adv/examine/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()

        if item == "WELL":  # Examining well gives binary code to be deciphered for next coin location
            if os.path.exists("hint.txt"):
                os.remove("hint.txt")
            desc = req['description']
            instructions = desc.split('\n')
            for line in instructions[117:]:
                # All commands before index 117 will just print "Mine your coin in room " before the number
                with open("hint.txt", "a") as f:
                    f.write(f"{line}\n")

            cpu = CPU()
            cpu.load('hint.txt')
            cpu.run()
            # clean up after itself and remove the hint file after used (new one will be made for future hints anyway)
            if os.path.exists("hint.txt"):
                os.remove("hint.txt")

            return cpu.hint
        else:
            print(req)

    def pray(self):
        time.sleep(self.cooldown)
        req = requests.post(f"{url}/api/adv/pray/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}).json()
        print(req)
        time.sleep(req['cooldown'])
        self.check_self()

    def check_balance(self):
        time.sleep(self.cooldown)
        req = requests.get(f"{url}/api/bc/get_balance/", headers={
            'Authorization': f"Token {key}"}).json()
        self.cooldown = req['cooldown']
        print(f"\n{req['messages'][0]}\n")
