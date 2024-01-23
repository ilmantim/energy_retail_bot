import logging

from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Customer  
from keyboard import main_menu_keyboard
from messages import HELLO


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MAIN_MENU = 0


def get_or_create_customer(update: Update, context: CallbackContext) -> tuple:
    user, created = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id
    )
    context.user_data['chat_id'] = user.chat_id
    return user, created


def check_user_bills(user) -> bool:
    if user.favorites.count() > 0:
        return True
    return False


def send_start_message(update: Update, has_bills: bool = False):
    if has_bills:
        update.message.reply_text(
            "Выберите раздел",
            reply_markup=main_menu_keyboard(True)
        )
    else:
        update.message.reply_text(
            "Выберите раздел",
            reply_markup=main_menu_keyboard()
        )


def handle_start(update: Update, context: CallbackContext) -> int:
    logger.info("start.py")

    if context.user_data.get('has_started', True):
        user, _ = get_or_create_customer(update, context)
        has_bills = check_user_bills(user)
        send_start_message(update, has_bills)
    else:
        context.user_data['has_started'] = True
        update.message.reply_text(HELLO)
        send_start_message(update)

    return MAIN_MENU
