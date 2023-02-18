from pony.orm import Database, set_sql_debug, db_session
from typing import Dict, List, Optional as type_optional
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

    def register_player_if_not_exist(self, user_id: int, name: str):
        with db_session:
            player = Player.get(id=str(user_id))
            if player is None:
                self.logger.info(
                    f"{user_id}:{name} is a new player with no record in DB"
                )
                new_player = Player(id=str(user_id), name=name, deck=Deck())
                self.logger.info(
                    f"{user_id}: {name} registered in DB"
                )
            else:
                self.logger.info(f"{user_id}: {name} already exists in DB")

    def add_card_to_user_deck(self, user: User, card_promt: str, card_path: str):
        with db_session:
            player = Player.get(id=str(user.id))
            if player is None:
                self.logger.error(
                    f"{user.id}:{user.first_name} added a card although he has no record in DB"
                )
            else:
                new_card = Card(
                    promt=card_promt,
                    author=player,
                    image_path=card_path,
                    deck=player.deck,
                )
                self.logger.info(
                    f"{user.id}:{user.first_name} added new card with id {new_card.id} to personal deck"
                )

    def get_player_cards(self, user: User) -> List[Card]:
        with db_session:
            player = Player.get(id=str(user.id))
            if player is None:
                self.logger.error(
                    f"{user.id}:{user.first_name} requested to view personal deck although he has no record in DB"
                )
            else:
                player_deck_cards = list(
                    select(card for card in Card if card.deck.id == player.deck.id)
                )
                self.logger.info(
                    f"{user.id}:{user.first_name} found {len(player_deck_cards)} in personal deck"
                )
                return player_deck_cards

    def get_user_card_path_by_id(self, user: User, card_id: int) -> type_optional[str]:
        with db_session:
            player = Player.get(id=str(user.id))
            if player is None:
                self.logger.error(
                    f"{user.id}:{user.first_name} requested to view card although he has no record in DB"
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

    def delete_player_card(self, user: User, card_id: int) -> bool:
        with db_session:
            player = Player.get(id=str(user.id))
            if player is None:
                self.logger.error(
                    f"{user.id}:{user.first_name} requested to delete card although he has no record in DB"
                )
            else:
                card_to_delete = Card.get(id=card_id)
                if card_to_delete is None:
                    self.logger.info(
                        f"{user.id}:{user.first_name} attempted to delete non existence card {card_id}, not deleting"
                    )
                    return False
                elif card_to_delete.author == player:
                    card_to_delete.delete()
                    self.logger.info(
                        f"{user.id}:{user.first_name} successfully deleted card {card_id}"
                    )
                    return True
                else:
                    self.logger.info(
                        f"{user.id}:{user.first_name} attempted to delete not their card {card_id}, not deleting"
                    )
                    return False

    def create_new_game(self, user_id: int):
        with db_session:
            player = Player.get(id=str(user_id))
            game = Game(players={player})
        self.logger.info(f"Game {game.id} created")
        with db_session:
            player = Player.get(id=str(user_id))
            player.game = Game.get(id=game.id)
        return game.id

    def add_user_to_game(self, user_id: int, game_id: int) -> type_optional[str]:
        print(f'adding to game: {game_id}')
        with db_session:
            player = Player.get(id=str(user_id))
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
                    return f"{player.first_name} {player.last_name}", [player.id for player in game.players]