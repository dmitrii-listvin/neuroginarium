from pony.orm import *
from typing import Dict


db = Database()


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    players = Set("Player")
    cards = Set("CardGameState")


class Deck(db.Entity):
    id = PrimaryKey(int, auto=True)
    player = Optional("Player")
    cards = Set("Card")


class Player(db.Entity):
    id = PrimaryKey(int)
    username = Required(str)
    game = Optional(Game)
    deck = Required(Deck)
    cards = Set("Card")
    game_owner = Set("CardGameState")
    score = Optional(int)
    is_current_player = Optional(bool)


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
    game_state = Optional("CardGameState")


class CardGameState(db.Entity):
    id = PrimaryKey(int, auto=True)
    game = Required(Game)
    card = Optional(Card)
    in_hand = Optional(Player)
    state = Required(str)