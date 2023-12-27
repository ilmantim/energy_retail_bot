import requests
import logging

from telegram import Update
from telegram.ext import CallbackContext

from commands.submit_readings import find_bill, send_info
from database import response_2, response_1
from retail.models import Bill, Customer, Favorite

from keyboard import yes_or_no_keyboard,\
    go_to_main_menu_keyboard,\
    submit_readnigs_and_get_meter_keyboard \
    
from commands.start import handle_start
from django.utils import timezone

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)


def get_meter_info(update: Update, context: CallbackContext) -> int:
    logger.info("Приборы учёта")
    text = update.message.text
    bills = Bill.objects.all()
    user, is_found = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id
    user_bills = Favorite.objects.filter(customer=user)

    if text == "В главное меню":
        return handle_start(update, context)
    elif text == "Как узнать лицевой счёт":
        update.message.reply_text(
            "Лицевой счёт указан в верхней части квитанции (извещение) рядом "
            "с Вашей фамилией \n",
        )
        update.message.reply_text(
            "Введите лицевой счёт",
            reply_markup=submit_readnigs_and_get_meter_keyboard())
        return METER_INFO

    try:
        if (text.isdigit() and not context.user_data['prev_step'] == 'choose') or (text.isdigit() and user_bills.filter(bill__value=bills.get(value=int(text)).value).exists()):
            context.user_data['prev_step'] = 'meter'
            find_bill(update, context)
            bill_here, is_found = Bill.objects.get_or_create(value=int(text))
            if user_bills.filter(bill__value=bill_here.value).exists():
                send_info(update, context)
            else:
                context.user_data['prev_step'] = 'meter'
                message = f'Адрес объекта - {bill_here.address}?'
                update.message.reply_text(message,
                                          reply_markup=yes_or_no_keyboard())
                return YES_OR_NO_ADDRESS
    except Bill.DoesNotExist:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не понял команду. Давайте начнем сначала.",
        )
        return METER_INFO
    except (requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError) as e:
        logger.info(f'A connection error occurred:{e}')

    if user.favorites.count() > 0 and not text == 'Ввести другой':
        bills_here = user.favorites.all()
        info = [[fav_bill.bill.value] for fav_bill in bills_here]
        update.message.reply_text("Выберите нужный пункт в меню снизу.",
                                  reply_markup=submit_readnigs_and_get_meter_keyboard(
                                      info))
        context.user_data['prev_step'] = 'choose'
        return digit_checker(update, context)
    else:
        info = None
        context.user_data['prev_step'] = 'meters'
        update.message.reply_text(
            "Введите лицевой счет",
            reply_markup=submit_readnigs_and_get_meter_keyboard(info)
        )
        return METER_INFO


def digit_checker(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user_here = Customer.objects.get(
        chat_id=int(context.user_data['chat_id']))
    if text in ["Как узнать лицевой счёт", "В главное меню", 'Ввести другой', 'Приборы учёта']:
        return METER_INFO
    elif text.isdigit() and user_here.favorites.filter(bill__value=int(text)).exists():
        return METER_INFO
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не понял команду. Давайте начнем сначала."
        )
        return METER_INFO