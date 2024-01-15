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

    text = update.message.text.lower()
    bill_here = Bill.objects.get(value=int(context.user_data['bill_num']))
    user_here = Customer.objects.get(chat_id=int(context.user_data['chat_id']))
    rate_here = bill_here.rates.get(id=context.user_data['rate'])

    registration_date_str = rate_here.registration_date.strftime("%Y-%m-%d") if rate_here.registration_date else "Не указана"
    readings_str = f'{rate_here.readings} квт*ч' if rate_here.readings is not None else "Не указаны"
    number_and_type_pu_str = bill_here.number_and_type_pu if bill_here.number_and_type_pu else "Не указаны"

    message = (
        f'Лицевой счет: {bill_here.value}\n'
        f'Номер и тип ПУ: {number_and_type_pu_str}\n'
        f'Показания: {readings_str}\n'
        f'Дата приёма: {registration_date_str}\n'
    )

    if text == 'да':
        bill_here.customers.add(user_here)
        Favorite.objects.create(customer=user_here, bill=bill_here, is_favorite=True)

    if text == 'нет':
        bill_here.customers.add(user_here)

    if text in ['да', 'нет']:
        if context.user_data['prev_step'] == 'submit':
            message += 'Введите новые показания:'
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return INPUT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            rates = bill_here.rates.all()
            for rate_here in rates:
                registration_date_str = (
                    rate_here.registration_date.date().strftime("%Y-%m-%d")
                    if rate_here.registration_date else "Дата не указана"
                )
                readings_str = str(
                    rate_here.readings) + ' квт*ч' if rate_here.readings is not None else "Показания не указаны"
                number_and_type_pu_str = bill_here.number_and_type_pu if bill_here.number_and_type_pu else "Номер и тип ПУ не указаны"
                if not rate_here == bill_here.rates.last():
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f'Лицевой счет: {bill_here.value}\n'
                             f'Номер и тип ПУ: {number_and_type_pu_str}\n'
                             f'Показания: {readings_str}\n'
                             f'Дата приёма: {registration_date_str}\n'
                    )
                else:
                    update.message.reply_text(
                        f'Лицевой счет: {bill_here.value}\n'
                        f'Номер и тип ПУ: {number_and_type_pu_str}\n'
                        f'Показания: {readings_str}\n'
                        f'Дата приёма: {registration_date_str}\n',
                        reply_markup=go_to_main_menu_keyboard()
                    )
                    return MAIN_MENU

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Не понял команду. Давайте попробуем снова.'
        )
        if context.user_data['prev_step'] == 'submit':
            return SUBMIT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            return METER_INFO
