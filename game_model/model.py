from pony.orm import *
from typing import Dict

db = Database()


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)


class Deck(db.Entity):
    id = PrimaryKey(int, auto=True)
    player = Optional("Player")
    cards = Set("Card")


class Player(db.Entity):
    id = PrimaryKey(str)
    # game = Optional(Game)
    deck = Required(Deck)
    cards = Set("Card")


# class PlayerGameState(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     game = Required(Game)
#     player = Required(Player)
#     score = Required(int)
#

class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    promt = Required(str)
    author = Required(Player)
    # image_storage = Required(str)
    image_path = Required(str)
    deck = Required(Deck)


# class CardGameState(db.Entity):
#     id = Required(str)
#     game = Required(Game)
#     card = Required(Card)
#     in_hand = Optional(PlayerGameState)
#     state = Required(str)


def bind_db(config: Dict):
    db_type = config["type"]
    db_params = config[db_type]
    db_params["provider"] = db_type
    db.bind(**db_params)
    db.generate_mapping(create_tables=True)
    set_sql_debug(True)
