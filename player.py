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
        self.inventory = data['inventory']
        self.abilities = data['abilities']
        self.status = data['status']
        self.has_mined = data['has_mined']
        self.errors = data['errors']
        self.messages = data['messages']
        self.current_room = self.check_room()
        self.world = "dark" if self.current_room['room_id'] > 499 else "light"
        self.map = self._read_file('map.txt')
        self.graph = self._read_file('graph.txt')

    def _get_status(self):
        r = requests.post(f"{url}/api/adv/status/",
                          headers={'Authorization': f"Token {key}", "Content-Type": "application/json"})
        return r.json()

    def _read_file(self, filepath):
        if self.world == 'dark':
            filepath = 'dark_' + filepath
        if not os.path.exists(filepath):
            f = open(filepath, 'w+')
            room = self.current_room
            if 'graph' in filepath:
                room = {room['room_id']: {d: '?' for d in room['exits']}}

            self._write_file(filepath, {self.current_room['room_id']: room})

        with open(filepath, 'r') as f:
            data = json.load(f)
            return data

    def _write_file(self, filepath, data):
        if self.world == 'dark' and 'dark' not in filepath:
            filepath = 'dark_' + filepath
        with open(filepath, 'w+') as outfile:
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
        self.abilities = data['abilities']
        self.status = data['status']
        self.has_mined = data['has_mined']
        self.errors = data['errors']
        self.messages = data['messages']
        self.map = self._read_file('map.txt')
        self.graph = self._read_file('graph.txt')

    def dash(self, direction, num_rooms, room_ids):
        if "dash" not in self.abilities:
            print("Error! You can't dash yet!")
            return
        time.sleep(self.cooldown)
        curr_id = self.current_room['room_id']
        print("\n===================")
        print(f"Dashing {direction} from room {curr_id}...")

        json = {"direction": direction,
                "num_rooms": num_rooms, "next_room_ids": room_ids}
        r = requests.post(f"{url}/api/adv/dash/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json)
        next_room = r.json()
        if 'players' in next_room:
            del next_room['players']
        next_id = next_room['room_id']

        # update map with room info
        self.map[next_id] = next_room
        self._write_file('map.txt', self.map)

        # change current room and update cooldown
        self.current_room = next_room
        self.cooldown = self.current_room['cooldown']

        for message in next_room['messages']:
            print(f"{message}")

        print(f"Now the player is in {self.current_room['room_id']}")
        print(f"Cooldown for dashing this time was {self.cooldown}")
        print("===================\n")

    def travel(self, direction, method="move"):
        time.sleep(self.cooldown)
        curr_id = self.current_room['room_id']

        print("\n===================")
        if "fly" in self.abilities and self.world != 'dark' and self.map[str(curr_id)]['elevation'] > 0:
            method = "fly"
            print(f"Flying {direction} from room {curr_id}...")
        else:
            print(f"Walking {direction} from room {curr_id}...")

        if direction not in self.graph[str(curr_id)]:
            print("Error! Not a valid direction from the current room")
        else:
            json = {"direction": direction}
            if self.graph[str(curr_id)][direction] != "?":
                json['next_room_id'] = str(self.graph[str(curr_id)][direction])
            next_room = requests.post(f"{url}/api/adv/{method}/", headers={
                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()

            # Code for looting any items in the room if the space is available
            if len(next_room['items']) > 0 and self.encumbrance < self.strength:
                for item in next_room['items']:
                    time.sleep(next_room['cooldown'])
                    self.pick_up_loot(item)

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

            for message in next_room['messages']:
                print(f"{message}")

            print(f"Now the player is in {self.current_room['room_id']}")
            print(f"Cooldown for moving this time was {self.cooldown}")
            if len(self.graph) < 500:
                print(
                    f"Total number of rooms explored so far: {len(self.graph)}")
        print("===================\n")

    def get_coin(self):
        time.sleep(self.cooldown)
        data = mine()
        self.cooldown = data['cooldown']
        if len(data['errors']) > 0:
            self.get_coin()

    def pick_up_loot(self, item):
        print(f"Looting {item}")
        json = {"name": item}
        if self.encumbrance < self.strength:
            time.sleep(self.cooldown)
            req = requests.post(f"{url}/api/adv/take/", headers={
                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
            print(req)
            self.cooldown = req['cooldown']
            time.sleep(self.cooldown)
        else:
            if "carry" in self.abilities:
                if len(self.status) != 0:
                    print(
                        "It seems your Bag is full and Glasowyn is already carring something!")
                else:
                    req = requests.post(f"{url}/api/adv/carry/", headers={
                        'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
                    self.cooldown = req['cooldown']
                    print(req)
            else:
                print("Your Bag is full!")

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
            print(req['description'])

    def pray(self):
        time.sleep(self.cooldown)
        req = requests.post(f"{url}/api/adv/pray/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}).json()
        print(req)
        time.sleep(req['cooldown'])
        self.check_self()

    def wear(self, item):
        time.sleep(self.cooldown)
        json = {"name": item}
        req = requests.post(f"{url}/api/adv/wear/", headers={
            'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()

        self.cooldown = req['cooldown']
        time.sleep(self.cooldown)
        self.check_self()

    def check_balance(self):
        time.sleep(self.cooldown)
        req = requests.get(f"{url}/api/bc/get_balance/", headers={
            'Authorization': f"Token {key}"}).json()
        self.coins = float(req['messages'][0].split(' ')[5])
        self.cooldown = req['cooldown']
        print(f"\n{req['messages'][0]}\n")

    def transform_coin(self, item):
        time.sleep(self.cooldown)
        self.check_balance()
        json = {"name": item}
        if self.coins > 0 and item in self.inventory:
            time.sleep(self.cooldown)
            req = requests.post(f"{url}/api/adv/transmogrify/", headers={
                                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
            print(req)
            self.cooldown = req['cooldown']
            for item in req['items']:
                self.pick_up_loot(item)

    def warp(self):
        if "warp" in self.abilities:
            time.sleep(self.cooldown)
            req = requests.post(f"{url}/api/adv/warp/", headers={
                                'Authorization': f"Token {key}", "Content-Type": "application/json"}).json()
            print(req)
            self.cooldown = req['cooldown']
            if self.world == 'light':
                self.world = 'dark'
            else:
                self.world = 'light'
        else:
            print("You do not have the warp ability yet!")
