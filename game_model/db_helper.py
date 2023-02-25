from pony.orm import Database, set_sql_debug, db_session
from typing import Dict, List, Optional as type_optional
import logging
from telegram import User
from .model import *


class DBHelper:
    def __init__(self, pony_db: Database, logger):
        self.db = pony_db
        self.logger = logger

    def bind_db(self, config: Dict):
        db_type = config["type"]
        db_params = config[db_type]
        db_params["provider"] = db_type
        self.db.bind(**db_params)
        self.db.generate_mapping(create_tables=True)
        set_sql_debug(True)

    def register_player_if_not_exist(self, user_id: int, username: str):
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.info(
                    f"{user_id}:{username} is a new player with no record in DB"
                )
                new_player = Player(id=user_id, username=username, deck=Deck())
                self.logger.info(
                    f"{user_id}: {username} registered in DB"
                )
            else:
                self.logger.info(f"{user_id}: {username} already exists in DB")

    def add_card_to_user_deck(self, user_id: int, card_promt: str, card_path: str):
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(
                    f"{user_id}: added a card although he has no record in DB"
                )
            else:
                new_card = Card(
                    promt=card_promt,
                    author=player,
                    image_path=card_path,
                    deck=player.deck,
                )
                self.logger.info(
                    f"{user_id}: added new card with id {new_card.id} to personal deck"
                )
                return new_card.id

    def get_player_cards(self, user_id: int) -> List[Card]:
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(
                    f"{user_id} requested to view personal deck although he has no record in DB"
                )
            else:
                player_deck_cards = list(
                    select(card for card in Card if card.deck.id == player.deck.id)
                )
                self.logger.info(
                    f"{user_id}: found {len(player_deck_cards)} in personal deck"
                )
                return player_deck_cards

    def get_user_card_path_by_id(self, user_id: int, card_id: int) -> type_optional[str]:
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(
                    f"{user_id}: requested to view card although he has no record in DB"
                )
                return None
            else:
                card = Card.get(id=card_id)
                if card is None:
                    return None
                elif card.author != player:
                    return None
                else:
                    return card.image_path

    def delete_player_card(self, user_id: int, card_id: int) -> bool:
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(
                    f"{user_id}: requested to delete card although he has no record in DB"
                )
            else:
                card_to_delete = Card.get(id=card_id)
                if card_to_delete is None:
                    self.logger.info(
                        f"{user_id}: attempted to delete non existence card {card_id}, not deleting"
                    )
                    return False
                elif card_to_delete.author == player:
                    card_to_delete.delete()
                    self.logger.info(
                        f"{user_id}: successfully deleted card {card_id}"
                    )
                    return True
                else:
                    self.logger.info(
                        f"{user_id}: attempted to delete not their card {card_id}, not deleting"
                    )
                    return False

    def create_new_game(self, user_id: int):
        with db_session:
            player = Player.get(id=user_id)
            game = Game(players={player})
        self.logger.info(f"Game {game.id} created")
        with db_session:
            player = Player.get(id=user_id)
            player.game = Game.get(id=game.id)
        return game.id

    def add_user_to_game(self, user_id: int, game_id: int) -> type_optional[str]:
        print(f'adding to game: {game_id}')
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(
                    f"{user_id} requested to join the game but he has no record in DB"
                )
                return None
            else:
                game = Game.get(id=game_id)
                if game is None:
                    self.logger.error(
                    f"{game_id}:no such game"
                )
                    return None
                else:
                    print(f'found the game! {game.id}')
                    game.players.add(player)
                    player.game = game
                    return player.username, [player.id for player in game.players]
    
    def start_user_game(self, user_id: int):
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(f"{user_id} requested to start the game but he has no record in DB")
            else:
                game = player.game
                if game is None:
                    self.logger.error(f"{user_id} requested to start the game but no game record in DB")
                else:
                    return [p.id for p in game.players]

    def kick_user(self, user_id: int, username_to_kick: str):
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(f"{user_id} /kick_user player not found")
            else:
                game = player.game
                if game is None:
                    self.logger.error(f"{user_id} /kick_user game not found")
                else:
                    if username_to_kick not in [p.username for p in game.players]:
                        return None
                    else:
                        kicked_player = [p for p in game.players if p.username == username_to_kick][0]
                        game.players = set((p for p in game.players if p.username != username_to_kick))
                        kicked_player.game = None
                        return kicked_player.id, [p.id for p in game.players]

    def leave_game(self, user_id: int):
        with db_session:
            player = Player.get(id=user_id)
            if player is None:
                self.logger.error(f"{user_id} /leave_game player not found")
            else:
                game = player.game
                if game is None:
                    self.logger.error(f"{user_id} /leave_game game not found")
                else:
                    game.players = set((p for p in game.players if p.id != user_id))
                    player.game = None
                    return [p.id for p in game.players]



def create_inmemory_db():
    logger = logging.getLogger(__name__)
    db_helper = DBHelper(db, logger)
    db_helper.bind_db({
        "type": "sqlite",
        "sqlite": {
            "filename": ":memory:",
            "create_db": True
            }
    })
    return db_helper