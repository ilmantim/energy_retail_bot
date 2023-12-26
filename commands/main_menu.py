import logging
from telegram import Update
from telegram.ext import CallbackContext
from commands.start import handle_start
from commands.submit_readings import submit_readings
from commands.get_meter_info import get_meter_info
from commands.get_contact_info import get_contact_info
from keyboard import main_menu_keyboard, show_bills_keyboard
from retail.models import Customer


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


MAIN_MENU, REMOVE_FAVORITE_BILLS = 0, 7


def handle_main_menu(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logger.info(f"Handling main menu: {text}")

    user = get_or_create_user(update.effective_chat.id)

    if text == "Мои лицевые счета" and user.favorites.exists():
        return display_user_bills(update, context, user)
    elif text == "Передать показания счётчиков":
        return submit_readings(update, context)
    elif text == "Приборы учёта":
        return get_meter_info(update, context)
    elif text == "Контакты и режим работы":
        return get_contact_info(update, context)
    elif text == "В главное меню":
        return go_to_main_menu(update, user)
    else:
        return handle_unknown_command(update, user)
    

def get_or_create_user(chat_id):
    return Customer.objects.get_or_create(chat_id=chat_id)[0]


def display_user_bills(update, context, user):
    user_bills = [
        str(favorite.bill.value) for favorite in user.favorites.all()
    ]
    message = 'Ваши лицевые счета:\n' + '\n'.join(user_bills)
    update.message.reply_text(message, reply_markup=show_bills_keyboard())
    context.user_data['prev_step'] = 'choose'
    return REMOVE_FAVORITE_BILLS


def go_to_main_menu(update, user):
    has_favorites = user.favorites.exists()
    update.message.reply_text(
        "Выберите раздел", 
        reply_markup=main_menu_keyboard(has_favorites)
    )
    return MAIN_MENU


def handle_unknown_command(update, user):
    has_favorites = user.favorites.exists()
    update.message.reply_text(
        "Не понял команду. Давайте начнем сначала.", 
        reply_markup=main_menu_keyboard(has_favorites)
    )
    return MAIN_MENU


def fallback(update: Update, context: CallbackContext) -> int:
    logger.warning("Fallback triggered for an unknown command")
    update.message.reply_text(
        "Не понял команду. Давайте начнем сначала.", 
        reply_markup=main_menu_keyboard()
    )
    return handle_start(update, context)