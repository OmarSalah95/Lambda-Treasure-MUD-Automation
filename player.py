from api import url, key
import requests
import json


class Player:
    def __init__(self, data):
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

    def check_room(self):
        r = requests.get(f"{url}/api/adv/init/",
                         headers={'Authorization': f"Token {key}"})
        data = r.json()
        del data['players']
        return data

    # def travel(self, direction, showRooms=False):
    #     nextRoom = self.currentRoom.getRoomInDirection(direction)
    #     if nextRoom is not None:
    #         self.currentRoom = nextRoom
    #         if (showRooms):
    #             nextRoom.printRoomDescription(self)
    #     else:
    #         print("You cannot move in that direction.")
