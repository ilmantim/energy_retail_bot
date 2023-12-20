import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import CallbackContext
    
from retail.models import Customer
from django.utils import timezone

from commands.start import handle_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
      ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def fill_readings(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text == "В главное меню":
        return handle_start(update, context)
    elif text.isdigit():
        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        bill_here = user_here.bills.get(
            value=int(context.user_data['bill_num']))
        if bill_here.readings:
            readings_1 = bill_here.readings
            readings_2 = int(text)
            subtraction = readings_2 - readings_1
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Ваш расход составил {subtraction} квт*ч'
            )
        bill_here.readings = int(text)
        bill_here.registration_date = timezone.now()
        bill_here.save()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Показания сохранены.'
        )
        return handle_start(update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='ты где то зафейлил'
        )