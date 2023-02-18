import pytest

from game_model.db_helper import DBHelper
from game_model.model import db, Player
import logging
from pony.orm import db_session

@pytest.fixture(scope="module")
def db_helper():
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

@pytest.fixture(scope="module")
def db_helper_with_one_user(db_helper: DBHelper):
    new_user_id = 1
    db_helper.register_player_if_not_exist(user_id=new_user_id, name='Test Testovich')
    return db_helper


def test_before_user_register(db_helper: DBHelper):
    new_user_id = 1
    with db_session:
        player = Player.get(id=str(new_user_id))
    assert player is None


def test_after_user_register(db_helper_with_one_user: DBHelper):
    with db_session:
        player = Player.get(id=str(1))
    assert player is not None


def test_creating_new_game(db_helper_with_one_user: DBHelper):
    game_id = db_helper_with_one_user.create_new_game(user_id=1)
    assert game_id == 1