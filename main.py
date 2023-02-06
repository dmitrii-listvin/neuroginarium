import yaml
import logging
import importlib
from enum import Enum
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from GameModel.model import *

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

with open("config.yml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)
    print("Config read successful")

num_of_variants = config["generation_choices_cnt"]

image_getter_class_name = config["image_generation"]["image_getter_class"]
image_getter_module = importlib.import_module(f"ImageGetter.{image_getter_class_name}")
image_getter_class = getattr(image_getter_module, image_getter_class_name)
image_getter = image_getter_class(
    config["image_generation"]["image_height"],
    config["image_generation"]["image_width"],
)

image_storage_class_name = config["file_system"]["image_storage_class"]
image_storage_module = importlib.import_module(
    f"ImageStorage.{image_storage_class_name}"
)
image_storage_class = getattr(image_storage_module, image_storage_class_name)
image_storage = image_storage_class(config["file_system"]["local"]["base_path"])

db_type = config["database"]["type"]
db_params = config["database"][db_type]
db_params["provider"] = db_type
db.bind(**db_params)
db.generate_mapping(create_tables=True)
set_sql_debug(True)

class DialogState(Enum):
    MENU, CARD, CHOOSE_CARD, PERSONAL_DECK_CHOICE = range(4)


MENU_CREATE_NEW_CARD = "Create new card"
MENU_VIEW_DECK = "View deck"
MENU_DONE = "Done"

menu_keyboard = [
    [MENU_CREATE_NEW_CARD, MENU_VIEW_DECK],
    [MENU_DONE],
]


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Start conversation with /start")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the menu."""
    user = update.message.from_user

    logger.info(f"{user.id}:{user.first_name} started /start")

    with db_session:
        player = Player.get(id=str(user.id))
        if player is None:
            logger.info(
                f"{user.id}:{user.first_name} is a new player with no record in DB"
            )
            new_player_deck = Deck()
            new_player = Player(id=str(user.id), deck=new_player_deck)
            # commit()
            logger.info(
                f"{user.id}:{user.first_name} registered in DB with deck id {new_player_deck.id}"
            )
        else:
            logger.info(f"{user.id}:{user.first_name} already exists in DB")

    await update.message.reply_text(
        "Hi! My name is Neuroginarium bot. Select an option from menu:\n\n"
        "Send /cancel to stop talking to me.",
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True),
    )

    return DialogState.MENU


async def generate_card_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Explain user to write a promt"""
    user = update.message.from_user
    logger.info(f"{user.first_name} requested to generate card")

    await update.message.reply_text(
        "Write your promt to generate card, or 'menu' to return to menu",
    )

    return DialogState.CARD


async def generate_card_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Generate cards and let user choose."""
    user = update.message.from_user
    logger.info("Promt of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text("Generating card variants, please wait...")
    images = await image_getter.get_n_cards(update.message.text, num_of_variants)

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
            [[str(i + 1) for i in range(num_of_variants)], ["None"]],
            one_time_keyboard=True,
        ),
    )

    return DialogState.CHOOSE_CARD


async def add_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's choice card (add in deck in future)"""
    user = update.message.from_user
    text = update.message.text
    logger.info(f"{user.first_name} selected {text}")

    choice_number = int(text) - 1
    selected_image = context.user_data["card_choices"][choice_number]

    saved_path = await image_storage.save_image(selected_image)

    logger.info(
        f"{user.id}:{user.first_name} chosen number {choice_number}; image saved to {saved_path}"
    )

    with db_session:
        player = Player.get(id=str(user.id))
        if player is None:
            logger.error(
                f"{user.id}:{user.first_name} added a card although he has no record in DB"
            )
        else:
            new_card = Card(
                promt=context.user_data["promt"],
                author=player,
                image_storage=image_storage_class_name,
                image_path=saved_path,
                deck=player.deck,
            )
            # commit()
            logger.info(
                f"{user.id}:{user.first_name} added new card with id {new_card.id} to personal deck"
            )

    await update.message.reply_photo(
        photo=selected_image, caption="you added this card!"
    )

    return await generate_card_menu(update, context)


async def view_deck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generate card and show it to user."""
    user = update.message.from_user
    logger.info(f"{user.id}:{user.first_name} requested to view personal deck")

    with db_session:
        player = Player.get(id=str(user.id))
        if player is None:
            logger.error(
                f"{user.id}:{user.first_name} requested to view personal deck although he has no record in DB"
            )
        else:
            player_deck_cards = list(
                select(card for card in Card if card.deck.id == player.deck.id)
            )
            logger.info(
                f"{user.id}:{user.first_name} found {len(player_deck_cards)} in personal deck"
            )

    if len(player_deck_cards) == 0:
        await update.message.reply_text(
            "You have no cards in deck; Create one",
            reply_markup=ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True),
        )
        return DialogState.MENU
    else:
        cards_str = "\n".join(
            [f"id:{c.id}, promt:{c.promt}" for c in player_deck_cards]
        )
        await update.message.reply_text(
            f"Send id of your card to view it or 'None' to return to menu:\n\n{cards_str}"
        )
        return DialogState.PERSONAL_DECK_CHOICE


async def view_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info(f"{user.id}:{user.first_name} requested to view {text}")

    with db_session:
        card = Card.get(id=int(text))  # will be able to view others cards, lol
        if card is None:
            await update.message.reply_text(f"No cards with this id!")
        else:
            image = await image_storage.load_image(card.image_path)
            await update.message.reply_photo(photo=image)

    await update.message.reply_text(
        f"Send another id of your card to view it or 'None' to return to menu"
    )
    return DialogState.PERSONAL_DECK_CHOICE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(config["bot_token"]).build()
    application.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DialogState.MENU: [
                MessageHandler(filters.Regex(f"^{MENU_CREATE_NEW_CARD}$"), generate_card_menu),
                MessageHandler(filters.Regex(f"^{MENU_VIEW_DECK}$"), view_deck),
                MessageHandler(filters.Regex(f"^{MENU_DONE}$"), cancel),
            ],
            DialogState.CARD: [
                MessageHandler(filters.Regex("^menu$"), start),
                MessageHandler(
                    ~filters.Regex("^menu$") & filters.TEXT & ~filters.COMMAND,
                    generate_card_answer,
                ),
            ],
            DialogState.CHOOSE_CARD: [
                MessageHandler(filters.Regex("^\d$"), add_card),
                MessageHandler(filters.Regex("^None$"), generate_card_menu),
            ],
            DialogState.PERSONAL_DECK_CHOICE: [
                MessageHandler(filters.Regex("^\d$"), view_card),
                MessageHandler(filters.Regex("^None$"), start),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
