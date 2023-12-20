import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram import Update
from telegram.ext import CallbackContext

from retail.models import Bill, Customer, Favorite

from keyboard import yes_or_no_keyboard,\
    go_to_main_menu_keyboard,\
    submit_readnigs_and_get_meter_keyboard \
    
from commands.start import handle_start

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
      ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def get_meter_info(update: Update, context: CallbackContext) -> int:
    logger.info("Приборы учёта")
    bills = Bill.objects.all()
    text = update.message.text
    user, is_found = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id
    if text.isdigit() and bills.filter(value=int(text)).exists():
        context.user_data['bill_num'] = text
        bill_here = bills.get(value=int(text))
        user_bills = Favorite.objects.filter(customer=user)
        if user_bills.filter(bill__value=bill_here.value).exists():
            update.message.reply_text(
                f'Лицевой счет: {bill_here.value}\n'
                f'Номер и тип ПУ: {bill_here.number_and_type_pu}\n'
                f'Показания: {bill_here.readings} квт*ч\n'
                f'Дата приёма: {bill_here.registration_date}\n',
                reply_markup=go_to_main_menu_keyboard()
            )
            return MAIN_MENU
        else:
            context.user_data['prev_step'] = 'meter'
            message = f'Адрес объекта - {bill_here.address}?'
            update.message.reply_text(message,
                                      reply_markup=yes_or_no_keyboard())
            return YES_OR_NO_ADDRESS

    if text == "В главное меню":
        return handle_start(update, context)

    user_here = Customer.objects.get(
        chat_id=int(context.user_data['chat_id']))
    if user_here.favorites.count() > 0 and not text == 'Ввести другой':
        bills_here = user_here.favorites.all()
        info = [[fav_bill.bill.value] for fav_bill in bills_here]
        update.message.reply_text("Выберите нужный пункт в меню снизу.",
                                  reply_markup=submit_readnigs_and_get_meter_keyboard(
                                      info))
        return METER_INFO

    elif text == "Как узнать лицевой счёт":
        update.message.reply_text(
            "Лицевой счёт указан в верхней части квитанции (извещение) рядом "
            "с Вашей фамилией \n Введите лицевой счет:",
            reply_markup=submit_readnigs_and_get_meter_keyboard())
        return METER_INFO
    else:
        info = None
        update.message.reply_text(
            "Введите лицевой счет",
            reply_markup=submit_readnigs_and_get_meter_keyboard(info)
        )
        return METER_INFO