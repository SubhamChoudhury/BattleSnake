import os
import random
import snakebrain
import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    game_id = ""
    turn = -1

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "Subham_Choudhury",  
            "color": "#E80978",  
            "head": "smile",  
            "tail": "hook",  
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json

        self.turn = data["turn"]
        self.game_id = data["game"]["id"]

        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        data = cherrypy.request.json

        self.turn = data["turn"]
        self.game_id = data["game"]["id"]
        body = data["you"]["body"]

        # Choose a direction to move in
        possible_moves = ["up", "down", "left", "right"]

        smart_moves = snakebrain.get_smart_moves(possible_moves, body, data["board"])

        move = random.choice(smart_moves)

        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        return "ok"

if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.thread.pool": 10})
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")), }
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
