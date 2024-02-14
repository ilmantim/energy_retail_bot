import logging

from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Rate

from keyboard import go_to_main_menu_keyboard
from commands.start import handle_start

from datetime import timedelta


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

(MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,
 CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS, BEFORE_INPUT_READINGS) = range(9)


def before_input_readings(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    if context.user_data['prev_step'] == 'fav' or text.isdigit():
        rate_here = Rate.objects.get(id=context.user_data['rates_ids'][0])
        device_here = rate_here.device
        bill_here = device_here.bill
        device_title = device_here.device_title
        modification = device_here.modification
        serial_number = device_here.serial_number
        readings_str = f'{rate_here.readings} квт*ч' if rate_here.readings is not None else "Не указаны"
        if rate_here.registration_date:
            # Add one day to the registration_date
            adjusted_date = rate_here.registration_date + timedelta(days=1)
            # Convert the adjusted date to a string in the desired format
            registration_date_str = adjusted_date.strftime("%d.%m.%Y")
        else:
            registration_date_str = "Не указана"

        #registration_date_str = rate_here.registration_date.strftime(
        #    "%d.%m.%Y") if rate_here.registration_date else "Не указана"
        message = (
            f'📋 Информация о лицевом счете:\n' 
            f'-----------------------------------\n'
            f'- Лицевой счет: {bill_here.value}\n'
            f'- Номер и тип прибора учета: {device_title} - {modification} (№{serial_number})\n'
            f'- Дата передачи последнего показания: {registration_date_str}\n'
            f'- Последнее показание: {readings_str}\n'
            f'- Тариф: {rate_here.cost}\n'
            f'-----------------------------------\n'
            f'Введите показание:'
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
