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

from telegram.ext.filters import MessageFilter

class ForwardedFromBot(MessageFilter):
    def filter(self, message):
        return message.forward_from.username == 'neuroginarium_dev_bot'

class GameplayHandler:
    def __init__(self, db_helper: DBHelper) -> None:
        self.db_helper = db_helper

    def __call__(self):
        return ConversationHandler(
            entry_points=[
                CommandHandler("new_game", self.new_game),
                MessageHandler(filters.FORWARDED & filters.TEXT & ForwardedFromBot(), self.forward_invite)
                ],
            states={
                "NEW_STATE": []
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            )

    async def new_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start new game."""
        new_game = self.db_helper.create_new_game(update.message.from_user)

        await update.message.reply_text(
            f"New game was created."
        )
        await update.message.reply_text(
            f"Forward this message to bot /join {new_game.id}"
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

    async def forward_invite(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """join a game"""
        text = update.message.text

        game_id = int(text[text.find('/join') + len('/join '):])
        new_player_name, all_users = self.db_helper.add_user_to_game(update.message.from_user, game_id)
        for user_id in all_users:
            await context.bot.send_message(int(user_id), f"{new_player_name} joined the game.")

