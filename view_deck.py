from enum import Enum
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
from game_model.db_helper import DBHelper
from image_getter import ImageGetter
from image_storage import ImageStorage
from game_model.model import *

logger = logging.getLogger(__name__)

class ViewDeckState(Enum):
    MENU, CARD, CHOOSE_CARD, PERSONAL_DECK_CHOICE = range(4)


class Menu:
    CREATE_NEW_CARD = "Create new card"
    VIEW_DECK = "View deck"
    DONE = "Done"

    keyboard = [
        [CREATE_NEW_CARD, VIEW_DECK],
        [DONE],
    ]


class ViewDeckHandler:
    def __init__(self, image_getter: ImageGetter, image_storage: ImageStorage, db_helper: DBHelper, num_of_variants: int) -> None:
        self.image_getter = image_getter
        self.image_storage = image_storage
        self.db_helper = db_helper
        self.num_of_variants = num_of_variants

    def __call__(self):
        return ConversationHandler(
            entry_points=[CommandHandler("deck", self.deck)],
            states={
                ViewDeckState.MENU: [
                    MessageHandler(filters.Regex(f"^{Menu.CREATE_NEW_CARD}$"), self.generate_card_menu),
                    MessageHandler(filters.Regex(f"^{Menu.VIEW_DECK}$"), self.view_deck),
                    MessageHandler(filters.Regex(f"^{Menu.DONE}$"), self.cancel),
                ],
                ViewDeckState.CARD: [
                    MessageHandler(filters.Regex("^menu$"), self.deck),
                    MessageHandler(
                        ~filters.Regex("^menu$") & filters.TEXT & ~filters.COMMAND,
                        self.generate_card_answer,
                    ),
                ],
                ViewDeckState.CHOOSE_CARD: [
                    MessageHandler(filters.Regex("^\d$"), self.add_card),
                    MessageHandler(filters.Regex("^None$"), self.generate_card_menu),
                ],
                ViewDeckState.PERSONAL_DECK_CHOICE: [
                    MessageHandler(filters.Regex("^\d$"), self.view_card),
                    MessageHandler(filters.Regex("^delete \d$"), self.delete_card),
                    MessageHandler(filters.Regex("^None$"), self.deck),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            )

    @staticmethod
    async def deck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the menu."""
        await update.message.reply_text(
            "Select an option from menu:\n\n"
            "Send /cancel to stop talking to me.",
            reply_markup=ReplyKeyboardMarkup(Menu.keyboard, one_time_keyboard=True),
        )

        return ViewDeckState.MENU

    @staticmethod
    async def generate_card_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Explain user to write a promt"""
        user = update.message.from_user
        logger.info(f"{user.username} requested to generate card")

        await update.message.reply_text(
            "Write your promt to generate card, or 'menu' to return to menu",
        )

        return ViewDeckState.CARD


    async def generate_card_answer(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Generate cards and let user choose."""
        user = update.message.from_user
        logger.info("Promt of %s: %s", user.username, update.message.text)

        await update.message.reply_text("Generating card variants, please wait...")
        images = await self.image_getter.get_n_cards(update.message.text, self.num_of_variants)

        context.user_data["card_choices"] = images
        context.user_data["promt"] = update.message.text

        media_group = [
            InputMediaPhoto(media=image, caption=str(i + 1))
            for i, image in enumerate(images)
        ]

        await update.message.reply_media_group(media=media_group)

        await update.message.reply_text(
            "Choose the best of cards:",
            reply_markup=ReplyKeyboardMarkup(
                [[str(i + 1) for i in range(self.num_of_variants)], ["None"]],
                one_time_keyboard=True,
            ),
        )

        return ViewDeckState.CHOOSE_CARD


    async def add_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show user's choice card (add in deck in future)"""
        user = update.message.from_user
        text = update.message.text
        logger.info(f"{user.first_name} selected {text}")

        choice_number = int(text) - 1
        selected_image = context.user_data["card_choices"][choice_number]

        saved_path = await self.image_storage.save_image(selected_image)

        logger.info(
            f"{user.id}:{user.username} chosen number {choice_number}; image saved to {saved_path}"
        )

        self.db_helper.add_card_to_user_deck(user.id, context.user_data["promt"], saved_path)

        await update.message.reply_photo(
            photo=selected_image, caption="you added this card!"
        )

        return await self.generate_card_menu(update, context)


    async def view_deck(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Generate card and show it to user."""
        user = update.message.from_user
        logger.info(f"{user.id}:{user.username} requested to view personal deck")

        player_deck_cards = self.db_helper.get_player_cards(user.id)

        if len(player_deck_cards) == 0:
            await update.message.reply_text(
                "You have no cards in deck; Create one",
                reply_markup=ReplyKeyboardMarkup(Menu.keyboard, one_time_keyboard=True),
            )
            return ViewDeckState.MENU
        else:
            cards_str = "\n".join(
                [f"id:{c.id}, promt:{c.promt}" for c in player_deck_cards]
            )
            await update.message.reply_text(
                f"You deck contents:\n\n{cards_str}"
            )
            await update.message.reply_text(
                f"Send id of your card to view it \n"
                f"Send 'delete <id>' to delete your card \n"
                f"or 'None' to return to menu"
            )
            return ViewDeckState.PERSONAL_DECK_CHOICE


    async def view_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        text = update.message.text
        logger.info(f"{user.id}:{user.username} requested to view {text}")

        card_path = self.db_helper.get_user_card_path_by_id(user.id, int(text))
        if card_path is None:
            await update.message.reply_text(f"No cards with this id!")
        else:
            image = await self.image_storage.load_image(card_path)
            await update.message.reply_photo(photo=image)

        await update.message.reply_text(
            f"Send another id of your card to view it \n"
            f"Send 'delete <id>' to delete your card \n"
            f"or 'None' to return to menu"
        )
        return ViewDeckState.PERSONAL_DECK_CHOICE


    async def delete_card(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        text = update.message.text
        logger.info(f"{user.id}:{user.username} requested to {text}")

        id_to_delete = int(text.split(" ")[1])
        if self.db_helper.delete_player_card(user.id, id_to_delete):
            await update.message.reply_text(f"Card with id {id_to_delete} is removed from your deck")
        else:
            await update.message.reply_text(f"No card with id {id_to_delete} found")

        await update.message.reply_text(
            f"Send another id of your card to view it \n"
            f"Send 'delete <id>' to delete your card \n"
            f"or 'None' to return to menu"
        )
        return ViewDeckState.PERSONAL_DECK_CHOICE

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.username)
        await update.message.reply_text(
            "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

