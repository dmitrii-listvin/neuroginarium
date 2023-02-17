import yaml
import logging
from telegram import (
    Update,
    User
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from game_model.model import *
from game_model.db_helper import DBHelper
from image_getter import *
from image_storage import *

from view_deck import ViewDeckHandler
from gameplay import GameplayHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

with open("config.yml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)
    print("Config read successful")

num_of_variants = config["generation_choices_cnt"]

image_getter = ImageGetter.build(config["image_generation"])
image_storage = ImageStorage.build(config["file_system"])

db_helper = DBHelper(db, logger)
db_helper.bind_db(config["database"])


def user2player(user: User) -> Player:
    return Player.get(id=str(user.id))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Start conversation with /start")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the menu."""
    user = update.message.from_user

    logger.info(f"{user.id}:{user.first_name} started /start")

    db_helper.register_player_if_not_exist(user)

    await update.message.reply_text(
"""Hi! My name is Neuroginarium bot. I understand command:
    /deck to create new cards or view existing
    /new_game to launch a new game
    /join to join existing game"""
    )


def main() -> None:
    application = Application.builder().token(config["bot_token"]).build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start))

    application.add_handler(ViewDeckHandler(image_getter, image_storage, db_helper, num_of_variants)())
    application.add_handler(GameplayHandler(db_helper)())
    

    application.run_polling()


if __name__ == "__main__":
    main()
