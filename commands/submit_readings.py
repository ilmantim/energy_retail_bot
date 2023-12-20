import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Mro, Bill, Customer
from datetime import datetime
from keyboard import yes_or_no_keyboard,\
    go_to_main_menu_keyboard,\
    submit_readnigs_and_get_meter_keyboard

from commands.start import handle_start    

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
    ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def submit_readings(update: Update, context: CallbackContext) -> int:
    logger.info("Передать показания счётчиков")
    bills = Bill.objects.all()
    text = update.message.text
    user, is_found = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id

    if text == "В главное меню":
        return handle_start(update, context)

    elif text == "Как узнать лицевой счёт":
        update.message.reply_text(
            "Лицевой счёт указан в верхней части квитанции (извещение) рядом "
            "с Вашей фамилией \n Введите лицевой счет:",
            reply_markup=submit_readnigs_and_get_meter_keyboard())
        return SUBMIT_READINGS

    today = datetime.now()
    if 15 <= today.day <= 25:
        if text.isdigit() and bills.filter(value=int(text)).exists():
            context.user_data['bill_num'] = text
            bill_here = bills.get(value=int(text))
            user_bills = user.bills.all()
            if user_bills.filter(value=bill_here.value).exists():
                update.message.reply_text(
                    f'Лицевой счет: {bill_here.value}\n'
                    f'Номер и тип ПУ: {bill_here.number_and_type_pu}\n'
                    f'Показания: {bill_here.readings} квт*ч\n'
                    f'Дата приёма: {bill_here.registration_date}\n'
                    'Введите новые показания:',
                    reply_markup=go_to_main_menu_keyboard()
                )
                return FILL_READINGS
            else:
                context.user_data['prev_step'] = 'submit'
                message = f'Адрес объекта - {bill_here.address}?'
                update.message.reply_text(message,
                                          reply_markup=yes_or_no_keyboard())
                return YES_OR_NO_ADDRESS

        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        if user_here.bills.count() > 0 and not text == 'Ввести другой':
            bills_here = user_here.favorites.all()
            info = [[fav_bill.bill.value] for fav_bill in bills_here]
            update.message.reply_text("Выберите нужный пункт в меню снизу.",
                                      reply_markup=submit_readnigs_and_get_meter_keyboard(
                                          info))
        else:
            info = None
            update.message.reply_text("Введите лицевой счёт",
                                      reply_markup=submit_readnigs_and_get_meter_keyboard(
                                          info))
        return SUBMIT_READINGS

    else:
        update.message.reply_text(
            "Показания принимаются с 15 по 25 число каждого месяца.")
        return MAIN_MENU