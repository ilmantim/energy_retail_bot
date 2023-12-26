import logging
from telegram import Update
from telegram.ext import CallbackContext

from retail.models import Bill, Customer, Favorite
from keyboard import go_to_main_menu_keyboard
from commands.start import handle_start


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)


MAIN_MENU, INPUT_READINGS, METER_INFO = 0, 2, 4


def construct_message(bill):
    registration_date_str = bill.registration_date.date().strftime("%d.%m.%Y") if bill.registration_date else "Не указана"
    readings_str = f'{bill.readings} квт*ч' if bill.readings is not None else "Не указаны"
    number_and_type_pu_str = bill.number_and_type_pu if bill.number_and_type_pu else "Не указаны"

    return (
        f'Лицевой счет: {bill.value}\n'
        f'Номер и тип ПУ: {number_and_type_pu_str}\n'
        f'Показания: {readings_str}\n'
        f'Дата приёма: {registration_date_str}\n'
    )


def create_favorite_bill(update: Update, context: CallbackContext) -> int:
    logger.info("create_favorite_bill")

    text = update.message.text.lower()
    user_id = int(context.user_data['chat_id'])
    bill_num = int(context.user_data['bill_num'])
    
    try:
        bill_here = Bill.objects.get(value=bill_num)
        user_here = Customer.objects.get(chat_id=user_id)
    except Bill.DoesNotExist:
        logger.error(f"Bill not found: {bill_num}")
        return MAIN_MENU  
    except Customer.DoesNotExist:
        logger.error(f"Customer not found: {user_id}")
        return MAIN_MENU  

    bill_here.customers.add(user_here)
    
    if text in ['да', 'нет']:
        if text == 'да':
            Favorite.objects.create(
                customer=user_here, bill=bill_here, is_favorite=True
            )

        message = construct_message(bill_here)
        message += 'Введите новые показания:' if context.user_data['prev_step'] == 'submit' else ''
        
        update.message.reply_text(
            message, reply_markup=go_to_main_menu_keyboard()
        )
        return INPUT_READINGS if context.user_data['prev_step'] == 'submit' else METER_INFO

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не выбрали ответ'
        )
        return handle_start(update, context)