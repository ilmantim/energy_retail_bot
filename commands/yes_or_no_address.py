import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()


from telegram import Update
from telegram.ext import CallbackContext
    
from keyboard import yes_or_no_keyboard

from commands.start import handle_start
 

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
      ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def yes_or_no_address(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text.lower() == 'нет':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Проверьте правильность введения номера лицевого счета.\n"
                 "Возможно, по данному адресу приборы учёта отсутствуют или закончился срок поверки.\n"
                 "Для уточнения информации обратитесь к специалисту контакт-центра"
        )
        return handle_start(update, context)
    elif text.lower() == 'да':
        update.message.reply_text(
            "Вы хотите добавить этот лицевой счёт в избранное?",
            reply_markup=yes_or_no_keyboard()
        )
        return ADD_TO_FAVORITE
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Это сообщение вы видите, если не ответили да/нет'
        )
        if context.user_data['prev_step'] == 'submit':
            return SUBMIT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            return METER_INFO
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='ты где то зафейлил'
            )