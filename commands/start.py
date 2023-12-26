import logging
from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Customer
from keyboard import main_menu_keyboard
from messages import HELLO


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)


MAIN_MENU = 0


def handle_start(update: Update, context: CallbackContext) -> int:
    logger.info("Start command triggered")

    user = get_or_create_user(update, context)
    has_favorites = user.favorites.exists()
    context.user_data['bills_count'] = user.favorites.count() if has_favorites else 0

    send_welcome_message(update, context, has_favorites)
    return MAIN_MENU


def get_or_create_user(update: Update, context: CallbackContext):
    user, _ = Customer.objects.get_or_create(chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id
    return user


def send_welcome_message(
        update: Update, context: CallbackContext, has_favorites: bool
):
    if context.user_data.get('has_started', False):
        context.user_data['has_started'] = True
        update.message.reply_text(HELLO)
    
    update.message.reply_text(
        "Выберите раздел", reply_markup=main_menu_keyboard(has_favorites)
    )