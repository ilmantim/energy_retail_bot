import logging

from telegram import Update
from telegram.ext import CallbackContext
    
from retail.models import Bill, Customer, Favorite
from keyboard import go_to_main_menu_keyboard


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)


def create_favorite_bill(update: Update, context: CallbackContext) -> int:
    logger.info("create_favorite_bill")

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
            return INPUT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return METER_INFO

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
            return INPUT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return METER_INFO

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Это сообщение вы видите, если не ответили да/нет'
        )
        if context.user_data['prev_step'] == 'submit':
            return SUBMIT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            return METER_INFO
