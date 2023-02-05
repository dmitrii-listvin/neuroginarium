import yaml
import logging
import importlib
import uuid
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
image_storage_module = importlib.import_module(f"ImageStorage.{image_storage_class_name}")
image_storage_class = getattr(image_storage_module, image_storage_class_name)
image_storage = image_storage_class(
    config["file_system"]["local"]["base_path"]
)

MENU, CARD, CHOOSE_CARD = range(3)

menu_keyboard = [
    ["Create new card", "View deck - not ready"],
    ["Done"],
]


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Start conversation with /start")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the menu."""

    await update.message.reply_text(
        "Hi! My name is Neuroginarium bot. Select an option from menu:\n\n"
        "Send /cancel to stop talking to me.",
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True),
    )

    return MENU


async def generate_card_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Explain user to write a promt"""
    user = update.message.from_user
    logger.info(f"{user.first_name} requested to generate card")

    await update.message.reply_text(
        "Write your promt to generate card, or 'menu' to return to menu",
    )

    return CARD


async def generate_card_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Generate cards and let user choose."""
    user = update.message.from_user
    logger.info("Promt of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text("Generating card variants, please wait...")
    images = await image_getter.get_n_cards(update.message.text, num_of_variants)

    context.user_data["card_choices"] = images

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

    return CHOOSE_CARD


async def add_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's choice card (add in deck in future)"""
    user = update.message.from_user
    text = update.message.text
    logger.info(f"{user.first_name} selected {text}")

    choice_number = int(text) - 1
    selected_image = context.user_data["card_choices"][choice_number]

    await image_storage.save_image(selected_image, f"{user.id}/{uuid.uuid4()}.png")

    await update.message.reply_photo(
        photo=selected_image, caption="you added this card!"
    )

    return await generate_card_menu(update, context)


async def view_deck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generate card and show it to user."""
    user = update.message.from_user
    logger.info(f"{user.first_name} requested to view deck")

    await update.message.reply_text(
        "Sorry, this feature is coming soon",
        reply_markup=ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True),
    )

    return MENU


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
            MENU: [
                MessageHandler(filters.Regex("^Create new card$"), generate_card_menu),
                MessageHandler(filters.Regex("^View deck - not ready$"), view_deck),
                MessageHandler(filters.Regex("^Done$"), cancel),
            ],
            CARD: [
                MessageHandler(filters.Regex("^menu$"), start),
                MessageHandler(
                    ~filters.Regex("^menu$") & filters.TEXT & ~filters.COMMAND,
                    generate_card_answer,
                ),
            ],
            CHOOSE_CARD: [
                MessageHandler(filters.Regex("^\d$"), add_card),
                MessageHandler(filters.Regex("^None$"), generate_card_menu),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
