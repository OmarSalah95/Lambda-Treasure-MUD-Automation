url = "https://lambda-treasure-hunt.herokuapp.com"
key = open("api_key.txt", "r").read()
opposite = {"n": "s", "e": "w", "s": "n", "w": "e"}


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
                if player.graph[last_room][direction] != '?':
                    path_copy = p.copy()
                    path_copy.append(player.graph[last_room][direction])
                    q.enqueue(path_copy)