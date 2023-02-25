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

LOBBY_STATE = "LOBBY"
PLAYING_STATE = "PLAYING"

class ForwardedFromBot(MessageFilter):
    def filter(self, message):
        return message.forward_from.username == 'neuroginarium_dev_bot' # move to config or del

class GameplayHandler:
    def __init__(self, db_helper: DBHelper) -> None:
        self.db_helper = db_helper

    def __call__(self):
        return ConversationHandler(
            entry_points=[
                CommandHandler("new_game", self.new_game),
                CommandHandler("join", self.join),
                MessageHandler(filters.FORWARDED & filters.TEXT & ForwardedFromBot(), self.join)
                ],
            states={
                LOBBY_STATE: [
                    CommandHandler("start_game", self.start_game),
                ],
                PLAYING_STATE: [
                    CommandHandler("kick_user", self.kick_user),
                    CommandHandler("leave_game", self.leave_game),
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            )

    async def new_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start new game."""
        new_game_id = self.db_helper.create_new_game(update.message.from_user.id)

        await update.message.reply_text(
            f"New game was created.\n/start_game to start the game"
        )
        await update.message.reply_text(
            f"Forward this message to bot /join {new_game_id}"
        )

        return LOBBY_STATE # so far only creator can start the game

    async def join(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Join the game."""
        text = update.message.text
        game_id = int(text[text.find('/join') + len('/join '):])
        new_player_username, all_users = self.db_helper.add_user_to_game(update.message.from_user.id, game_id)
        for user_id in all_users:
            await context.bot.send_message(user_id, f"{new_player_username} joined the game.")

        return PLAYING_STATE

    async def start_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the game."""
        
        all_users = self.db_helper.start_user_game(update.message.from_user.id)
        for user_id in all_users:
            await context.bot.send_message(user_id, "Game is started:")

        # call game deck creation

        return PLAYING_STATE

    async def kick_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        text = update.message.text
        username = text[text.find('/kick_user') + len('/kick_user '):] # shoud write this format in help or something
        replay = self.db_helper.kick_user(update.message.from_user.id, username)
        if replay is None:
            await context.bot.send_message(update.message.from_user.id, "no such username in your game (try without @)")
        else:
            kicked_user_id, remaining_users = replay
            await context.bot.send_message(kicked_user_id, f"you was kicked from the game.")
            for user_id in remaining_users:
                await context.bot.send_message(user_id, f"{username} was kicked from the game.")
        return PLAYING_STATE

    async def leave_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: # shoud write about this commant in help or something
        remaining_users = self.db_helper.leave_game(update.message.from_user.id)
        await context.bot.send_message(update.message.from_user.id, "you left the game.")
        for user_id in remaining_users:
            await context.bot.send_message(user_id, f"{update.message.from_user.username} left the game.")
        return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.username)
        await update.message.reply_text(
            "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END
