import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Customer

from keyboard import main_menu_keyboard,\
    show_bills_keyboard

from commands.submit_readings import submit_readings
from commands.get_meter_info import get_meter_info
from commands.get_contact_info import get_contact_info

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
    ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)



def handle_main_menu(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logger.info("Главное меню")

    if text == "Мои лицевые счета" and context.user_data['bills_count']:
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        user_bills = [str(bill.value) for bill in user.bills.all()]
        all_bills = '\n'.join(user_bills)
        message = 'Ваши лицевые счета:\n' + all_bills
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        update.message.reply_text(
            "Выберите нужный пункт снизу.",
            reply_markup=show_bills_keyboard()
        )
        return MANAGE_DELETE
    if text == "Передать показания счётчиков":
        return submit_readings(update, context)
    elif text == "Приборы учёта":
        return get_meter_info(update, context)
    elif text == "Контакты и режим работы":
        return get_contact_info(update, context)
    elif text == "В главное меню":
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        if user.favorites.count() > 0:
            context.user_data['bills_count'] = user.favorites.count()
            bills = True
        else:
            bills = False
        update.message.reply_text("Выберите раздел",
                                  reply_markup=main_menu_keyboard(bills))
        return MAIN_MENU
    else:
        update.message.reply_text("Не понял команду. Давайте начнем сначала.",
                                  reply_markup=main_menu_keyboard())
        return MAIN_MENU
    

def fallback(update: Update, context: CallbackContext) -> int:
    logger.warning("Неизвестная команда")
    update.message.reply_text("Не понял команду. Давайте начнем сначала.",
                              reply_markup=main_menu_keyboard())
    return MAIN_MENU