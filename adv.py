import requests
import json
import random
import time

from player import Player

from api import url, key, opposite, Queue
player = Player()

def get_name(name):

    # Make list of treasure rooms
    treasure_rooms = []
    for k, v in player.map.items():
        if "tiny treasure" in v["items"]:
            treasure_rooms.append(k)
    treasure_rooms[len(treasure_rooms)//2:]
    print("The following rooms have treasure:", treasure_rooms)

    while player.gold < 1000:  # This is automatically updated, otherwise have to check server
        while player.encumbrance < player.strength:
            # find room with treasure
            # go there
            print
            current_treasure_room = treasure_rooms[0]
            travel_to_target(int(current_treasure_room))

            # pick up treasure
            # while there are still items to pick up:
            # while len(player.map[str(player.current_room["room_id"])]["items"]) > 0:
            player.pick_up_loot("tiny treasure")

            # update map entry for room to reflect taken treasure
            player.map[current_treasure_room]["items"] = []
            player._write_file('map.txt', player.map)
            treasure_rooms = treasure_rooms[1:]

            # If all treasure in map has been taken, go straight to shop
            if len(treasure_rooms) < 1:
                break

        # travel to shop
        # sell all items in inventory
        sell_loot()
        player.check_self()
    # travel to Pirate Ry's
    travel_to_target(467)
    # purchase name
    player.buy_name(name)


def sell_loot():
    travel_to_target(1)
    time.sleep(player.cooldown)
    print(player.inventory)
    for item in player.inventory:
        print("in for loop")
        json = {"name": item}
        print(json)
        r1 = requests.post(f"{url}/api/adv/sell/", headers={'Authorization': f"Token {key}",
                                                            "Content-Type": "application/json"}, json=json).json()
        time.sleep(r1['cooldown'])
        json['confirm'] = "yes"
        r1_conf = requests.post(f"{url}/api/adv/sell/", headers={
                                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
        print(r1_conf)
        time.sleep(r1_conf['cooldown'])


def explore_random():
    """
    Returns a random unexplored exit direction from the current room
    """
    directions = player.current_room["exits"]
    room_id = str(player.current_room["room_id"])
    unexplored = [d for d in directions if player.graph[room_id][d] == '?']
    return unexplored[random.randint(0, len(unexplored)-1)]


def dft_for_dead_end():
    """
    Performs depth-first traversal to explore random unexplored paths until
    finding a dead end (either no other exits at all, or no unexplored exits)
    """
    while '?' in list(player.graph[str(player.current_room["room_id"])].values()):
        # Grab direction that leads to unexplored exit
        next_dir = explore_random()
        # Travel there
        player.travel(next_dir)


def generate_path(target):
    """
    Performs BFS to find shortest path to target room. If "?" passed instead of target room id,
    finds closest room with an unexplored exit.
    Returns the first path to meet the specified criteria.
    """
    # Create an empty queue and enqueue a PATH to the current room
    q = Queue()
    q.enqueue([str(player.current_room["room_id"])])
    # Create a Set to store visited rooms
    v = set()

    while q.size() > 0:
        p = q.dequeue()
        last_room = str(p[-1])
        if last_room not in v:
            # Check if target among exits (either a "?" or specific ID)
            if target in list(player.graph[last_room].values()):
                # >>> IF YES, RETURN PATH (excluding starting room)
                if target != "?":
                    p.append(target)
                return p[1:]
            # Else mark it as visited
            v.add(last_room)
            # Then add a PATH to its neighbors to the back of the queue
            for direction in player.graph[last_room]:
                if player.graph[last_room][direction] != '?':
                    path_copy = p.copy()
                    path_copy.append(player.graph[last_room][direction])
                    q.enqueue(path_copy)


def travel_to_target(target='?'):
    """
    Runs a BFS to specific room or to nearest room with unexplored exit,
    then moves through that path in order.
    """
    if player.current_room["room_id"] == target:
        return
    bfs_path = generate_path(target)
    print(f"new path to follow! {bfs_path}")
    while bfs_path is not None and len(bfs_path) > 0:
        next_room = bfs_path.pop(0)
        current_id = str(player.current_room["room_id"])
        next_direction = next(
            (k for k, v in player.graph[current_id].items() if v == next_room), None)
        player.travel(next_direction)


def explore_maze():
    """
    While the player's map is shorter than the number of rooms, continue looping
    through DFT until a dead end OR already fully-explored room is found,
    then perform BFS to find shortest path to room with unexplored path and go there.
    """
    while len(player.graph) < 500:
        dft_for_dead_end()
        travel_to_target()
    print("Map complete!")


def acquire_powers():
    """
    After maze has been generated, now go to shrines and acquire powers by praying.
    Order of importance is flight -> dash -> everything else if ready.
    """
    if "fly" not in player.abilities:
        shrine = 22
        travel_to_target(shrine)
        player.pray()
    if "dash" not in player.abilities:
        shrine = 461
        travel_to_target(shrine)
        player.pray()
    if "carry" not in player.abilities:
        shrine = 499
        travel_to_target(shrine)
        player.pray()
    if "warp" not in player.abilities:
        shrine = 374
        travel_to_target(shrine)
        player.pray()
    # if "dash" not in player.abilities:
    #     dash_shrine = 486
    #     travel_to_target(dash_shrine)
    #     player.pray()
    print(f"Your Abilities are now: {player.abilities}")


def sell_loot():
    travel_to_target(1)
    time.sleep(player.cooldown)
    print(player.inventory)
    for item in player.inventory:
        json = {"name": item}
        r1 = requests.post(f"{url}/api/adv/sell/", headers={'Authorization': f"Token {key}",
                                                            "Content-Type": "application/json"}, json=json).json()
        time.sleep(r1['cooldown'])
        json['confirm'] = "yes"
        r1_conf = requests.post(f"{url}/api/adv/sell/", headers={
                                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
        print(r1_conf)
        time.sleep(r1_conf['cooldown'])
        player.check_self()


def get_rich():
    while True:
        # travel to wishing well
        travel_to_target(55)
        # examine it to get the new hint
        new_room = player.examine('WELL')
        print(f"Next coin can be mined in room {new_room}\n")
        travel_to_target(int(new_room))
        player.get_coin()
        player.check_balance()


if __name__ == '__main__':
    running = True
    command_list = {
        "moveTo": {"call": player.travel, "arg_count": 1},
        "buildMap": {"call": explore_maze, "arg_count": 0},
        "travelTo": {"call": travel_to_target, "arg_count": 1},
        "loot": {"call": player.pick_up_loot, "arg_count": 1},
        "drop": {"call": player.drop_loot, "arg_count": 1},
        "mine": {"call": player.get_coin, "arg_count": 0},
        "pray": {"call": player.pray, "arg_count": 0},
        "wear": {"call": player.wear, "arg_count": 1},
        "checkSelf": {"call": player.check_self, "arg_count": 0},
        "sellLoot": {"call": sell_loot, "arg_count": 0},
        "roomDeets": {"call": player.check_room, "arg_count": 0},
        "checkCoins": {"call": player.check_balance, "arg_count": 0},
        "getName": {"call": get_name, "arg_count": 1},
        "examine": {"call": player.examine, "arg_count": 1},
        "getRich": {"call": get_rich, "arg_count": 0},
        "getPowers": {"call": acquire_powers, "arg_count": 0},
        "transmogrify": {"call": player.transform_coin, "arg_count": 1},
    }

    while running:
        user_data = input('Enter command: ').split(' ')

        cmd = user_data[0]
        args = user_data[1:]

        for i, v in enumerate(args):
            if v.isdigit():
                args[i] = int(v)

        if cmd == 'quit':
            running = False

        elif cmd not in command_list:
            print("That Command is not part of our command list try again.")

        else:
            if command_list[cmd]["arg_count"] == 1:
                command_list[cmd]['call'](
                    " ".join(args) if len(args) > 1 else args[0])
            elif command_list[cmd]["arg_count"] == 0:
                command_list[cmd]['call']()

        # command_list[cmd]()
    # player.travel('n')
    # player.travel('s')
    # explore_maze()
    # travel_to_target(79)
    # player.pick_up_loot('tiny treasure')
    # print(player.inventory)
    # player.drop_loot('tiny treasure')
    # print(player.inventory)
