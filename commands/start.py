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


MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)


def handle_start(update: Update, context: CallbackContext) -> int:
    logger.info("кнопка_старт")

    if context.user_data.get('has_started', True):
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        context.user_data['chat_id'] = user.chat_id
        if user.favorites.count() > 0:
            context.user_data['bills_count'] = user.favorites.count()
            bills = True
        else:
            bills = False
        update.message.reply_text("Выберите раздел",
                                  reply_markup=main_menu_keyboard(bills))
    else:

        context.user_data['has_started'] = True
        update.message.reply_text(HELLO)

        update.message.reply_text(
            "Выберите раздел",
            reply_markup=main_menu_keyboard()
        )
    return MAIN_MENU
