import requests
import json
import random
import time
# from util import Stack, Queue
from player import Player
from api import url, key, opposite





class Queue():
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None

    def size(self):
        return len(self.queue)


def explore_random():
    """
    Returns a random unexplored exit direction from the current room
    Used to get MVP goal of final graph traversal <2000 moves (clocked in ~1000)
    Overall inefficient since it will sometimes take the longest paths first and have to journey all the way back to the shorter dead end branches
    """
    directions = player.current_room["exits"]
    room_id = str(player.current_room["room_id"])
    unexplored = [d for d in directions if player.graph[room_id][d] == '?']
    return unexplored[random.randint(0, len(unexplored)-1)]

# def origin(direction):
#     """
#     Small util function returning the opposite of a direction
#     used in quickly determining the origin direction when a player arrives in a new room
#     """
#     opposite = {"n": "s", "e": "w", "s": "n", "w": "e"}
#     return opposite[direction]

# # Create empty graph with initial room (0)
# map ={0:{}}
# for direction in world.startingRoom.getExits():
#     map[0][direction] = '?'


def dft_for_dead_end():
    # while '?' in list(map[player.currentRoom.id].values()):
    # current_id = player.current_room["room_id"]
    while '?' in list(player.graph[str(player.current_room["room_id"])].values()):
        # current_id = player.current_room["room_id"]
        # Grab direction that leads to unexplored exit
        next_dir = explore_random()
        # if only one unexplored direction, always go there
        # unexplored_rooms =[]
        # for key, val in list(map[player.currentRoom.id].items()):
        #     if val == '?':
        #         unexplored_rooms.append(key)
        # if len(unexplored_rooms) == 1:
        #     next_dir = unexplored_rooms[0]
        # otherwise, search down the multiple possibilities and go down the one that has the fewest unexplored rooms (typically a dead end branch)
        # else:
        #     next_dir = explore_shortest()
        #     if next_dir == None:
        #         break
        # Change current room's exit in that direction to the next room
        # map[player.currentRoom.id][next_dir] = player.currentRoom.getRoomInDirection(next_dir).id
        # Add travel direction to traversal path
        # traversalPath.append(next_dir)
        # Travel there
        player.travel(next_dir)
        # if player.currentRoom.id not in map:
        #     map[player.currentRoom.id] = {}
        # if len(map[player.currentRoom.id]) <1:
        #     for direction in player.currentRoom.getExits():
        #         map[player.currentRoom.id][direction] = '?'
        # mark previous room as explored direction
        # map[player.currentRoom.id][origin(next_dir)] = current_id


def generate_path(target):
    """
    Performs BFS to find shortest path to room with unexplored exit from current location
    Returns the first path to meet this criteria
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
            # Check if it has unexplored rooms
            print(target)
            print(list(player.graph[last_room].values()))
            
            if target in list(player.graph[last_room].values()):
                # >>> IF YES, RETURN PATH (excluding starting room) so player can go travel shortest path to room with unexplored exit
                if target != "?":
                    # final_dir = next(
                    #     (k for k, v in player.graph[last_room].items() if str(v) == target), '?')
                    # final_dir ='?'
                    
                    
                    
                    # for d in player.graph[last_room]:
                    #     if player.graph[last_room][d] is target:
                    #         final_dir=d
                    
                    p.append(target)
                    print(p[1:])
                return p[1:]
            # Else mark it as visited
            v.add(last_room)
            # Then add a PATH to its neighbors to the back of the queue
            for direction in player.graph[last_room]:
                if player.graph[last_room][direction] !='?':
                    path_copy = p.copy()
                    path_copy.append(player.graph[last_room][direction])
                    q.enqueue(path_copy)


def travel_to_target(target='?'):
    """
    Once a room with no unexplored exits is reached, run a BFS to find
    the shortest path to a room with an unexplored exit for each room in
    that path, then move that direction and log the movement in the traversal path
    """

    bfs_path = generate_path(target)
    while bfs_path is not None and len(bfs_path) > 0:
        next_room = bfs_path.pop(0)
        current_id = str(player.current_room["room_id"])
        # next_direction = next((k for k, v in map[player.currentRoom.id].items() if v == next_room), None)
        next_direction = next(
            (k for k, v in player.graph[current_id].items() if v == next_room), None)
        player.travel(next_direction)

# # def travel_to_nearest_unexplored():
# #     travel_to_target('?')


def explore_maze():
    """
    While the player's map is shorter than the number of rooms, continue looping
    through DFT until a dead end OR already fully-explored room is found,
    then perform BFS to find shortest path to room with unexplored path and go there
    """
    # while len(map) < len(roomGraph):
    while len(player.graph) < 500:
        dft_for_dead_end()
        travel_to_target()


# The actual maze traversal function
player = Player()

# player.travel('n')
# player.travel('s')
# explore_maze()
# travel_to_target(79)
player.pick_up_loot('tiny treasure')
print(player.inventory)
player.drop_loot('tiny treasure')
print(player.inventory)
# TRAVERSAL TEST
# visited_rooms = set()
# player.currentRoom = world.startingRoom
# visited_rooms.add(player.currentRoom)
# for move in traversalPath:
#     player.travel(move)
#     visited_rooms.add(player.currentRoom)

# if len(visited_rooms) == len(roomGraph):
#     print(f"TESTS PASSED: {len(traversalPath)} moves, {len(visited_rooms)} rooms visited")
# else:
#     print("TESTS FAILED: INCOMPLETE TRAVERSAL")
#     print(f"{len(roomGraph) - len(visited_rooms)} unvisited rooms")
