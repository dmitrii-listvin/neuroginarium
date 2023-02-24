import pytest

from game_model.db_helper import DBHelper, create_inmemory_db
from game_model.model import Player
from pony.orm import db_session

@pytest.fixture
def db_helper():
    db_helper = create_inmemory_db()
    yield db_helper
    db_helper.db.provider = db_helper.db.schema = None

@pytest.fixture
def db_helper_with_one_user(db_helper: DBHelper):
    new_user_id = 1
    db_helper.register_player_if_not_exist(user_id=new_user_id, name='Test Testovich')
    return db_helper


def test_before_user_register(db_helper: DBHelper):
    new_user_id = 1
    with db_session:
        player = Player.get(id=new_user_id)
    assert player is None


def test_after_user_register(db_helper_with_one_user: DBHelper):
    with db_session:
        player = Player.get(id=1)
    assert player is not None


def test_creating_new_game(db_helper_with_one_user: DBHelper):
    game_id = db_helper_with_one_user.create_new_game(user_id=1)
    assert game_id == 1

def test_update_user_game(db_helper_with_one_user: DBHelper):
    user_id = 1
    db_helper_with_one_user.create_new_game(user_id=user_id)
    last_game_id = db_helper_with_one_user.create_new_game(user_id=user_id)
    with db_session:
        player = Player.get(id=user_id)
    assert player.game.id == last_game_id

def test_join_game(db_helper_with_one_user: DBHelper):
    host_user_id = 1
    game_id = db_helper_with_one_user.create_new_game(user_id=host_user_id)

    new_user_id = 2
    joined_user_name='Joined User'
    db_helper_with_one_user.register_player_if_not_exist(user_id=new_user_id, name=joined_user_name)
    
    joined_user_name, game_users_ids = db_helper_with_one_user.add_user_to_game(user_id=new_user_id, game_id=game_id)
    
    assert joined_user_name == joined_user_name
    assert sorted(game_users_ids) == [host_user_id, new_user_id]

def test_join_non_existing_game(db_helper_with_one_user: DBHelper):
    host_user_id = 1
    game_id = db_helper_with_one_user.create_new_game(user_id=host_user_id)

    new_user_id = 2
    joined_user_name='Joined User'
    db_helper_with_one_user.register_player_if_not_exist(user_id=new_user_id, name=joined_user_name)
    
    assert db_helper_with_one_user.add_user_to_game(user_id=new_user_id, game_id=game_id + 1) is None
