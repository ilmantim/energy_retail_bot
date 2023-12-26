import logging

import requests
from telegram import Update
from telegram.ext import CallbackContext

from commands.digit_checker import digit_checker
from commands.find_bill import find_bill
from commands.send_info import send_info
from retail.models import Mro, Bill, Customer, Favorite
from datetime import datetime
from keyboard import yes_or_no_keyboard,\
    go_to_main_menu_keyboard,\
    submit_readnigs_and_get_meter_keyboard

from commands.start import handle_start    
from database import response_1, response_2
from django.utils import timezone

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)


def submit_readings(update: Update, context: CallbackContext) -> int:
    logger.info("Передать показания счётчиков")
    text = update.message.text
    user, is_found = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id
    # посылаем запрос, получаем ответ со счетом, если счет есть добавляем в БД
    bills = Bill.objects.all()
    if text == "В главное меню":
        context.user_data['prev_step'] = 'main'
        return handle_start(update, context)

    elif text == "Как узнать лицевой счёт":
        context.user_data['prev_step'] = 'get_bill'
        update.message.reply_text(
            "Лицевой счёт указан в верхней части квитанции (извещение) рядом "
            "с Вашей фамилией \n Введите лицевой счет:",
            reply_markup=submit_readnigs_and_get_meter_keyboard())
        return SUBMIT_READINGS

    today = datetime.now()
    user_bills = Favorite.objects.filter(customer=user)
    if 15 <= today.day <= 30:
        try:
            if (text.isdigit() and not context.user_data['prev_step'] == 'choose') or (text.isdigit() and user_bills.filter(bill__value=bills.get(value=int(text)).value).exists()):
                find_bill(update, context, text, SUBMIT_READINGS)
                bill_here = Bill.objects.get(value=int(text))
                if user_bills.filter(bill__value=bill_here.value).exists():
                    send_info(update, context, bill_here, submit=True)
                else:
                    context.user_data['prev_step'] = 'submit'
                    message = f'Адрес объекта - {bill_here.address}?'
                    update.message.reply_text(message,
                                              reply_markup=yes_or_no_keyboard())
                    return YES_OR_NO_ADDRESS
        except Bill.DoesNotExist:
            update.message.reply_text(
                "Не понял команду. Давайте начнем сначала."
            )
            return SUBMIT_READINGS
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError) as e:
            logger.info(f'A connection error occurred:{e}')

        if user.favorites.count() > 0 and not text == 'Ввести другой':
            print(context.user_data['prev_step'])
            bills_here = user.favorites.all()
            info = [[fav_bill.bill.value] for fav_bill in bills_here]
            update.message.reply_text("Выберите нужный пункт в меню снизу.",
                                      reply_markup=submit_readnigs_and_get_meter_keyboard(
                                          info))
            context.user_data['prev_step'] = 'choose'
            return digit_checker(update, context, SUBMIT_READINGS, user)
        else:
            info = None
            context.user_data['prev_step'] = 'enter_readings'
            update.message.reply_text("Введите лицевой счёт",
                                      reply_markup=submit_readnigs_and_get_meter_keyboard(
                                          info))
            return SUBMIT_READINGS

    else:
        update.message.reply_text(
            "Показания принимаются с 15 по 25 число каждого месяца.")
        return MAIN_MENU

