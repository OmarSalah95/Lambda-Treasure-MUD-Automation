import requests
import json
import random
import time

from player import Player
from api import url, key, opposite, Queue
player = Player()


def get_name(name):
    """
    Using the most recent locations of treasure, the player travels to those rooms
    and picks up items until inventory is full, then will automatically travel back to the shop and sell them.
    Once having sold 1000g worth of items at the shop, player will go to Pirate Ry's and
    purchase the specified name for themselves (needed for mining Lambda coins).
    """

    # Make list of treasure rooms
    treasure_rooms = []
    for k, v in player.map.items():
        if len(v["items"]) > 0:
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
     """
    Travels to shop and sells all items in inventory.
    """
    travel_to_target(1)
    time.sleep(player.cooldown)
    print('\nAll the items here in your bag shall be sold', player.inventory, "\n")
    for item in player.inventory:
        json = {"name": item}
        r1 = requests.post(f"{url}/api/adv/sell/", headers={'Authorization': f"Token {key}",
                                                            "Content-Type": "application/json"}, json=json).json()
        time.sleep(r1['cooldown'])
        json['confirm'] = "yes"
        r1_conf = requests.post(f"{url}/api/adv/sell/", headers={
                                'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json).json()
        print(f"Clerk: {r1_conf['messages'][0]}")
        print(f'{"*"*8} {r1_conf["messages"][1]} {"*"*8}\n')
        player.cooldown = r1_conf['cooldown']
        time.sleep(player.cooldown)
    player.check_self()


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
    q.enqueue([("placeholder direction", str(player.current_room["room_id"]))])
    # Create a Set to store visited rooms
    visited = set()

    while q.size() > 0:
        p = q.dequeue()
        last_room = p[-1]
        last_room_id = str(last_room[1])
        if last_room_id not in visited:
            # Check if target among exits (either a "?" or specific ID)
            for k, v in player.graph[last_room_id].items():
                if str(v) == str(target):
                    # >>> IF YES, RETURN PATH (excluding starting room)
                    if target != "?":
                        p.append((k, v))
                    return p[1:]
            # Else mark it as visited
            visited.add(last_room_id)
            # Then add a PATH to its neighbors to the back of the queue
            for k, v in player.graph[last_room_id].items():
                if v != '?':
                    path_copy = p.copy()
                    path_copy.append((k, v))
                    q.enqueue(path_copy)


def travel_to_target(target='?'):
    """
    Runs a BFS to specific room or to nearest room with unexplored exit,
    then moves through that path in order.
    """

    if player.current_room["room_id"] == target:
        return
    bfs_path = generate_path(target)
    print(f"\nNew path to follow! {bfs_path}\n")
    while bfs_path is not None and len(bfs_path) > 0:
        # check if there are consecutive matching directions (dash opportunity)

        if len(bfs_path) > 2 and bfs_path[0][0] == bfs_path[1][0] == bfs_path[2][0] and "dash" in player.abilities:
            print("Power coils in your legs as you prepare to dash!")
            dash_direction = bfs_path[0][0]
            dash_room_ids = []
            for move in bfs_path:
                # only grab the consecutive same directions, not later in the path list
                if move[0] == dash_direction:
                    dash_room_ids.append(str(move[1]))
                else:
                    break
            num_rooms = len(dash_room_ids)
            string_ids = ",".join(dash_room_ids)

            # if there are, submit dash request
            player.dash(dash_direction, str(num_rooms), string_ids)
            # update path to remove dashed rooms
            bfs_path = bfs_path[num_rooms:]
        # else, just move
        else:
            next_room = bfs_path.pop(0)
            next_direction = next_room[0]
            player.travel(next_direction)


def explore_maze():
    """
    While the player's map has any room with unexplored exit, continue looping
    through DFT until a dead end OR already fully-explored room is found,
    then perform BFS to find shortest path to room with unexplored path and go there.
    """
    f = 'dark_graph.txt' if player.world == 'dark' else 'graph.txt'
    graph = open(f).read().rstrip()
    while '?' in graph:
        dft_for_dead_end()
        travel_to_target()
    print("Map complete!")


def acquire_powers():
    """
    After maze has been generated, now go to shrines and acquire powers by praying.
    Order of importance is dash -> flight -> everything else if available.
    """
    if "dash" not in player.abilities:
        shrine = 461
        travel_to_target(shrine)
        player.pray()
    if "fly" not in player.abilities:
        shrine = 22
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
    print(f"Your Abilities are now: {player.abilities}")


def get_rich():
    """
    If in light world (start), player will continuously loop getting Lambda coin locations
    from the Wishing Well and going to that spot to mine them. Will also pick up any treasures along the way,
    and if inventory becomes full, will go to the shop to sell them, maximizing gold and LC profit.

    If in dark world, player will go to the dark Wishing Well, wait until a new snitch location has been revealed
    (means somebody else just got the last one), go there, and loot it. Player will perform a set amount of checks
    at the well and will go to the specified location regardless after reaching that count.
    """
    while True:
        if player.world == 'dark':
            print(f"\n{player.name} currently has {player.snitches} snitches!")
        if player.encumbrance >= player.strength:
            sell_loot()
        # travel to wishing well
        travel_to_target(55 if player.world == 'light' else 555)
        # examine it to get the new hint
        new_room = player.examine('WELL')
        if player.world == 'dark':
            print('Waiting for new snitch location...')
            head_start = player.examine('WELL')
            count = 0
            check_limit = 100
            while head_start == new_room and count < check_limit:
                head_start = player.examine('WELL')
                count += 1
                if count >= check_limit:
                    print(
                        "You can't wait here any longer. Go to the last known location!")
            new_room = head_start

        print(
            f"Next {'coin can be mined' if player.world == 'light' else 'snitch can be found'} in room {new_room}\n")
        if player.encumbrance >= player.strength:
            sell_loot()
        travel_to_target(int(new_room))
        if player.world == 'light':
            player.get_coin()
            player.check_balance()
        else:
            # player automatically loots a golden snitch anytime they come across it, either
            # from move or dash
            time.sleep(player.cooldown)
            player.check_self()


def get_leaderboard():
    """
    Travels to location of the gold leaderboard and prints it out.
    """
    time.sleep(player.cooldown)
    travel_to_target(486)
    player.examine('BOOK')


def transmogrify(item):
    """
    Tosses an acquired item and one Lambda Coin into the transmog in return for random gear.
    """
    time.sleep(player.cooldown)
    travel_to_target(495)
    player.transform_coin(item)


def print_map():
    """
    Prints an approximation of the built map in the REPL.
    """
    m = player.map
    g = player.graph
    row = [" "] * 100
    border = ["#"] * 155
    grid = [['     ' for i in range(31)] for j in range(100)]
    for i in [0, 1, 98, 99]:
        grid[i] = border.copy()

    for r_id in m:
        coords = m[r_id]['coordinates']
        x = int(coords[1:3])-45
        y = int(coords[-3:-1])
        has_e = 'e' in m[r_id]['exits'] and g[r_id]['e'] != "?"
        if has_e:
            grid[y][x] = str(r_id).zfill(3) + "--"
        else:
            grid[y][x] = str(r_id).zfill(3) + "  "

    for line in grid:
        print("".join(line))


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
        "getLeaderboard": {"call": get_leaderboard, "arg_count": 0},
        "transmogrify": {"call": transmogrify, "arg_count": 1},
        "warp": {"call": player.warp, "arg_count": 0},
        "showMap": {"call": print_map, "arg_count": 0}
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
