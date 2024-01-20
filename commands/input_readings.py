import logging

import requests
from telegram import Update
from telegram.ext import CallbackContext
    
from retail.models import Customer
from django.utils import timezone

from commands.start import handle_start


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS, BEFORE_INPUT_READINGS = range(9)


def input_readings(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text == "В главное меню":
        return handle_start(update, context)
    elif text.isdigit():
        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        bill_here = user_here.bills.get(
            value=int(context.user_data['bill_num']))
        rate_here = bill_here.rates.get(id=context.user_data['rate'])
        if rate_here.readings:
            readings_1 = rate_here.readings
            readings_2 = int(text)
            subtraction = readings_2 - readings_1
            k = readings_2 / readings_1
            if subtraction > 0 and k < 2:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f'Ваш расход составил {subtraction} квт*ч'
                )
            else:
                if subtraction < 0:
                    message = ('Значение не может быть отрицательным, '
                               'перепроверьте показания и попробуйте снова.')
                else:
                    message = ('Недопустимые данные, перепроверьте показания '
                               'и попробуйте снова.')
                update.message.reply_text(
                    message
                )
                return INPUT_READINGS
        rate_here.readings = int(text)
        rate_here.registration_date = timezone.now()
        rate_here.save()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Показания сохранены.'
        )
        data = {
            "id_device": bill_here.id_device,
            "id_receiving_method": 42,
            "id_reading_status": 6,
            "rates": [
                {
                    "id_tariff": rate_here.id_tariff,
                    "id_indication": rate_here.id_indication,
                    "reading": rate_here.readings
                }
            ]
        }

        url = 'https://lk-api.backspark.ru/api/v0/cabinet/terminal/submitReadings'
        response = requests.post(url, json=data)
        if response.status_code == 200:
            logger.info('Success!')
        else:
            logger.info('Error: %s', str(response.status_code))
        return handle_start(update, context)
    else:
        update.message.reply_text(
            "Не понял команду. Пожалуйста, введите новые показания:"
        )
        return INPUT_READINGS
