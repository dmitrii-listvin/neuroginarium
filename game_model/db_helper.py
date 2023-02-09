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

    def register_player_if_not_exist(self, user: User):
        with db_session:
            player = Player.get(id=str(user.id))
            if player is None:
                self.logger.info(
                    f"{user.id}:{user.first_name} is a new player with no record in DB"
                )
                new_player_deck = Deck()
                new_player = Player(id=str(user.id), deck=new_player_deck)
                self.logger.info(
                    f"{user.id}:{user.first_name} registered in DB with deck id {new_player_deck.id}"
                )
            else:
                self.logger.info(f"{user.id}:{user.first_name} already exists in DB")

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

    def get_card_path_by_id(self, card_id: int) -> type_optional[str]:
        with db_session:
            card = Card.get(id=card_id)  # will be able to view others cards, lol
            if card is None:
                raise
            else:
                return card.image_path
