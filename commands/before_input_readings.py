import logging
import pprint

import requests
from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Mro, Bill, Customer, Favorite, Rate, Device
from datetime import datetime
from keyboard import yes_or_no_keyboard, go_to_main_menu_keyboard, submit_readings_and_get_meter_keyboard
from commands.start import handle_start
from django.utils import timezone


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

(MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,
 CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS, BEFORE_INPUT_READINGS) = range(9)


def before_input_readings(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print("YO ARE HERE 2")
    if context.user_data['prev_step'] == 'fav' or text.isdigit():
        print("YO ARE HERE 3")
        print(context.user_data['non_deletable_rates_ids'])
        print(context.user_data['rates_ids'])
        rate_here = Rate.objects.get(id=context.user_data['rates_ids'][0])

        registration_date_str = rate_here.registration_date.strftime(
            "%Y-%m-%d") if rate_here.registration_date else "Не указана"
        readings_str = f'{rate_here.readings} квт*ч' if rate_here.readings is not None else "Не указаны"
        number_and_type_pu_str = rate_here.device.number_and_type_pu if rate_here.device.number_and_type_pu else "Не указаны"

        message = (
            f'Лицевой счет: {rate_here.device.bill.value}\n'
            f'Номер и тип ПУ: {number_and_type_pu_str} {rate_here.title}\n'
            f'Показания: {readings_str}\n'
            f'Дата приёма: {registration_date_str}\n'
            'Введите новые показания:'
        )
        update.message.reply_text(
            message,
            reply_markup=go_to_main_menu_keyboard()
        )
        return INPUT_READINGS
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Не понял команду. Давайте попробуем снова.'
        )
        if context.user_data['prev_step'] == 'submit':
            return SUBMIT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            return METER_INFO
        else:
            return handle_start(update, context)
