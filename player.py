from api import url, key, opposite
import requests
import json
import time


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
        time.sleep(self.cooldown)
        curr_id = self.current_room['room_id']
        print(f"Moving {direction} from room {curr_id}...")

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
            print(f"Now the player is in {self.current_room['room_id']}")
            print(
                f"Total number of rooms explored so far: {len(self.graph)}\n")
