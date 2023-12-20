import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import CallbackContext

from retail.models import Mro
from django.utils import timezone
from datetime import datetime
from keyboard import main_menu_keyboard, choose_MRO_keyboard,\
    choose_address_keyboard
from commands.start import handle_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
      ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def get_contact_info(update: Update, context: CallbackContext) -> int:
    global prev_department
    logger.info("Контакты и режим работы")
    text = update.message.text
    if text.isdigit() and prev_department:
        department_here = Mro.objects.get(name=prev_department)
        addresses = department_here.addresses.all()
        address_here = addresses.get(num=int(text))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=address_here.name
        )
        return handle_start(update, context)
    elif text == "Главное меню":
        logger.info("Returning to main menu")
        return handle_start(update, context)
    elif Mro.objects.filter(name=text).exists():
        department = Mro.objects.get(name=text)
        if department.addresses.count() > 0:
            addresses = [str(i + 1) for i in
                         range(department.addresses.count())]

            prev_department = department.name
            update.message.reply_text(
                department.general,
                reply_markup=choose_address_keyboard(addresses)
            )
            update.message.reply_text(
                "Выберите номер удобного для Вас МРО в меню снизу")
            return CONTACT_INFO
        else:
            update.message.reply_text(
                department.general,
                reply_markup=main_menu_keyboard()
            )
            return handle_start(update, context)
    else:
        update.message.reply_text(
            "Выберите МРО",
            reply_markup=choose_MRO_keyboard()
        )
        return CONTACT_INFO