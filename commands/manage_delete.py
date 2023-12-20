import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Customer

from keyboard import main_menu_keyboard,\
    show_bills_keyboard, delete_bills_keyboard

from commands.start import handle_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
    ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def manage_delete(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text.isdigit() and context.user_data['bills_count'] > 0:
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        user.bills.get(value=int(text)).delete()
        context.user_data['bills_count'] = user.favorites.count()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Личный счет удален из вашего списка.'
        )
        if user.favorites.count() > 0:
            bills = True
        else:
            bills = False
        update.message.reply_text("Выберите раздел",
                                  reply_markup=main_menu_keyboard(bills))
        return MAIN_MENU
    elif text == 'Назад':
        update.message.reply_text(
            "Выберите нужный пункт снизу.",
            reply_markup=show_bills_keyboard()
        )
        return MANAGE_DELETE
    elif text == 'Главное меню':
        return handle_start(update, context)
    elif text == "Удалить лицевой счёт":
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        user_bills = [str(bill.value) for bill in user.bills.all()]
        update.message.reply_text(
            "Выберите лицевой счёт, который Вы хотите удалить.",
            reply_markup=delete_bills_keyboard(user_bills)
        )
        return MANAGE_DELETE