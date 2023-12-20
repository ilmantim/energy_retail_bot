import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import CallbackContext
    
from retail.models import Bill, Customer, Favorite
from keyboard import go_to_main_menu_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
      ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def add_to_favorite(update: Update, context: CallbackContext) -> int:
    logger.info("add_to_favorite")
    
    text = update.message.text
    bill_here = Bill.objects.get(value=int(context.user_data['bill_num']))
    if text.lower() == 'да':
        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        bill_here.customers.add(user_here)
        Favorite.objects.create(
            customer=user_here,
            bill=bill_here,
            is_favorite=True
        )
        message = (
            f'Лицевой счет: {bill_here.value}\n'
            f'Номер и тип ПУ: {bill_here.number_and_type_pu}\n'
            f'Показания: {bill_here.readings} квт*ч\n'
            f'Дата приёма: {bill_here.registration_date}\n'
        )
        if context.user_data['prev_step'] == 'submit':
            message += 'Введите новые показания:'
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return FILL_READINGS
        elif context.user_data['prev_step'] == 'meter':
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return METER_INFO
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='ты где то зафейлил'
            )
    elif text.lower() == 'нет':
        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        bill_here.customers.add(user_here)
        message = (
            f'Лицевой счет: {bill_here.value}\n'
            f'Номер и тип ПУ: {bill_here.number_and_type_pu}\n'
            f'Показания: {bill_here.readings} квт*ч\n'
            f'Дата приёма: {bill_here.registration_date}\n'
        )
        if context.user_data['prev_step'] == 'submit':
            message += 'Введите новые показания:'
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return FILL_READINGS
        elif context.user_data['prev_step'] == 'meter':
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return METER_INFO
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='ты где то зафейлил'
            )
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