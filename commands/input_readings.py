import logging
import pprint

import os
from dotenv import load_dotenv

import requests
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from commands.before_input_readings import before_input_readings
from retail.models import Rate
from django.utils import timezone

from commands.start import handle_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO, \
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS, BEFORE_INPUT_READINGS = range(
    9)

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL')


def input_readings(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text == "В главное меню":
        return handle_start(update, context)
    elif text.isdigit():
        rate_here = Rate.objects.get(id=context.user_data['rates_ids'][0])
        if rate_here.readings:
            readings_1 = rate_here.readings
            readings_2 = int(text)
            subtraction = readings_2 - readings_1
            k = readings_2 / readings_1
            if subtraction > 0 and k <= 2:
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
        if len(context.user_data['rates_ids']) > 1:
            del context.user_data['rates_ids'][0]
            return before_input_readings(update, context)
        else:
            del context.user_data['rates_ids'][0]
            rates = [Rate.objects.get(id=id) for id in
                     context.user_data['non_deletable_rates_ids']]
            devices = list({rate.device for rate in rates})
            data = [
                {
                    "id_device": device.id_device,
                    "id_receiving_method": 60,
                    "id_reading_status": 6,
                    "rates": [
                        {
                            "id_tariff": rate.id_tariff,
                            "id_indication": rate.id_indication,
                            "reading": rate.readings
                        } for rate in device.rates.all()
                    ]
                } for device in devices
            ]
            url = f'{API_BASE_URL}/api/v0/cabinet/terminal/submitReadings'
            for device_data in data:
                response = requests.post(url, json=device_data)
                if response.status_code == 200:
                    logger.info('Success!')
                else:
                    logger.info('Error: %s', str(response.status_code))
            return ConversationHandler.END
    else:
        update.message.reply_text(
            "Не понял команду. Пожалуйста, введите новые показания:"
        )
        return INPUT_READINGS
