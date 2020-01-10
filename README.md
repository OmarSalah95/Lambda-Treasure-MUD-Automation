# idk-treasure-hunt

# Player actions
All player interactions are initiated by loading the command prompt by running `python adv.py` from root directory.
- Note that a valid API key in a `api_key.txt` file is required to submit any API requests.
- REPLY command prompt can be exited by running the `quit` command.


## Player methods
Executes a single command off the Player class instance.
`<command>` -- description

### Move
`moveTo <direction>` -- Player moves one room in given direction, if possible. Prints info and relevant messages about movement to the REPL.
- If the room in that direction is already known, uses that knowledge to acquire Wise Explorer cooldown bonus. 
- If the current terrain is "NORMAL" or "MOUNTAIN" and the player has the "fly" ability, will fly instead to get Flight cooldown bonus and avoid elevation penalties. 
- Will also loot any found items in the next room upon entering, if player inventory allows for it.

### Loot Item
`loot <item name>` -- Player attempts to pick up the named item from the current room and add it to their inventory.
- If player has the `carry` ability, will give heaviest item to ghost companion to lighten load to avoid being overencumbered.

### Drop Item
`drop <item name>` -- Player attempts to drop the named item in the current room and remove it from their inventory.

### Check Self
`checkSelf` -- Prints all current player info.

### Check Room
`roomDeets` -- Retrieves info on current room from the server, updating any relevant information such as items in room.

### Mine Lambda Coin
`mine` -- Attempts to mine a Lambda Coin in the current room. Retrieves last valid proof from the server (if in correct room), and uses blockchain model to perform proof-of-work algorithm to find valid proof for next block. If successful, one Lambda Coin is added to player's account.
- Player must have purchased a name before attempting to mine

### Check Lambda Coin Balance
`checkCoins` -- Shows current amount of Lambda Coins acquired.

### Equip Item
`wear <item>` -- Equips specififed item (either footwear or bodywear) if in inventory. Will remove currently worn item in that slot, if any.
- Equipment items are only acquirable at the transmogrifier
- Different qualities of footwear and bodywear may be acquired, allowing for more speed (lower cooldowns when traveling) and higher strength (can carry more items)

### Pray at Shrine
`pray` -- Player attempts to pray at current location. If at one of the game's shrines, will acquire a new power and have it added to their abilities.

### Warp to Alternate Dimension
`warp` -- If player has warp ability, will transport them to other world (light and dark worlds exist).

### Examine Item or Player
`examine <name>` -- Examines specified item in current room or inventory, or player in current room and prints info. If examining one of the Wishing Wells, player will receive a clue to the location of the next Lambda Coin (light world) or golden snitch (dark world).

### Show Map
`showMap` -- Builds a map from the player's current world and currently known rooms and prints it.


## Helper functions
Run one or more player methods to execute more complex functionality for more programmatic approach.
`<command>` -- description

### Build map
`buildMap` -- Map must be generated before other actions requiring full map can be implemented. Uses combination of Depth-first traversal to explore rooms until reaching a dead end (no other exits, or no unexplored exits), and a breadth-first search to then find the path to the nearest room that does have an unexplored exit. Loops until the generated graph does not have any "?" (unexplored) exits. 
- If 3+ given directions are the same in the currently executed BFS path (ex: "n", "n", "n"), player will automatically use the dash ability (if acquired) to achieve an overall lower travel time.
- Generates a world-specific `map.txt` file with all relevant room info.
- Generates a world-specific `graph.txt` file to be used as an adjacency list for traversal.
- Depending on player's current world (light/dark) will only use the relevant map data.

### Travel to Location
`travelTo <room number>` -- Uses same path generation and traversal used in `buildMap` function but with specified target. Player will travel to the specified room if it exists in their map.
- If room is in other world and warp ability is acquired, player will warp first before travelling.
- Uses same traversal algorithm as `buildMap` function, so player will dash through multiple rooms at once if appropriate.

### Sell All Loot
`sellLoot` -- Player will travel to the shop and sell all currently held loot in inventory in exchange for gold.

### Get Name
`getName <new name>` -- Player will travel to Pirate Ry's and exchange 1000g to change their name. If the player currently has less than 1000g, will use most recent map info to track rooms which contain treasures, travel to them and acquire them, and sell their inventory when full until 1000g is achieved.
- Player is required to have a new name before being able to mine Lambda Coins

### Transmogrify
`transmogrify <item>` -- Player will travel to the Transmogrifier if not already there and will remove the item from their inventory in exchange for a random piece of equipment. Each use also requires one Lambda Coin.

### Acquire Powers
`getPowers` -- Player will acquire all powers not currently held. Order of priority will be `dash` -> `fly` -> `carry` -> `warp`. Powers will be available for use and automatically used -- when applicable -- as soon as they are acquired.

### View Leaderboard
`getLeaderboard` -- Player will travel to room which contains leaderboard data and prints the current info to the screen.
- Only viewable leaderboard is for gold acquisition, not Lambda Coins or golden snitches

### Acquire Currency
`getRich` -- Player will continuously acquire the rare item of whichever world they are currently in. Loop repeats until REPL is quit.
- Light world -- Player will repeatedly travel to the Wishing Well, get the location of the next mineable Lambda Coin from the hint there, and travel to the location and mine the coin. Will still acquire items if encountered, and automatically go to the shop to sell their inventory if it becomes full. Lambda Coins are unique to each player so no other optimizations are required -- a coin will always be mineable at the most recently hinted location.
- Dark world -- Player will go to the Dark World's Wishing Well and check the current location of the golden snitch. Since snitches are ubiquitous and shared by everybody within the Treasure Hunt server, more competitive approach is required to increase chances of finding it. Player will therefore repeatedly check the snitch location hint and will only travel there the moment it changes, since that signifies that the last one was just looted. This ensures the player always has the biggest lead in getting to the next snitch. Since the player will automatically loot any golden snitches they find when moving/dashing to a room, will automatically pick it up once at the target destination. Also has a small chance to loot a snitch when travelling normally in the dark world, but happens rarely. If snitch not there by the time target room is reached, will print error message.