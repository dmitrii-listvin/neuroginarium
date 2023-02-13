import logging
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InputMediaPhoto,
    User
)
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from game_model.model import *
from game_model.db_helper import DBHelper

logger = logging.getLogger(__name__)


class GameplayHandler:
    def __init__(self, db_helper: DBHelper) -> None:
        self.db_helper = db_helper

    def __call__(self):
        return ConversationHandler(
            entry_points=[CommandHandler("new_game", self.new_game)],
            states={
                "NEW_STATE": []
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            )

    async def new_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the menu."""
        new_game = self.db_helper.create_new_game()

        await update.message.reply_text(
            f"New game {new_game.id} created."
        )

        return "NEW_STATE"


    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

