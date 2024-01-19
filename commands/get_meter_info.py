import logging
import requests
from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Bill, Customer, Favorite, Rate
from datetime import datetime
from keyboard import yes_or_no_keyboard, go_to_main_menu_keyboard, submit_readings_and_get_meter_keyboard
from commands.start import handle_start
from django.utils import timezone


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO, CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)
API_BASE_URL = "https://lk-api-dev.backspark.ru/api/v0/cabinet/terminal"
MAIN_MENU_COMMAND = "В главное меню"
GET_BILL_INFO_COMMAND = "Как узнать лицевой счёт"
READING_PERIOD_START = 15
READING_PERIOD_END = 25
MOSCOW_TIMEZONE_OFFSET = 180


def check_reading_period():
    today = datetime.now()
    return READING_PERIOD_START <= today.day <= READING_PERIOD_END


# в главное меню
def handle_main_menu(update: Update, context: CallbackContext):
    context.user_data['prev_step'] = 'main'
    return handle_start(update, context)

# как узнать номер лицевого счёта
def handle_get_bill_info(update: Update, context: CallbackContext, calling_context):
    context.user_data['prev_step'] = 'get_bill'
    update.message.reply_text(
        "Лицевой счёт указан в верхней части квитанции (извещение) рядом с Вашей фамилией \nВведите лицевой счёт:",
        reply_markup=submit_readings_and_get_meter_keyboard()
    )
    return METER_INFO if calling_context == 'get_meter_info' else SUBMIT_READINGS



def retrieve_bill_info(bill_id: str):
    #Функция получения id_PA  из API


def submit_readings(update: Update, context: CallbackContext) -> int:
    

def get_meter_info(update: Update, context: CallbackContext) -> int:
  

def digit_checker(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user = Customer.objects.get(chat_id=int(context.user_data['chat_id']))
    if text in [GET_BILL_INFO_COMMAND, MAIN_MENU_COMMAND, 'Ввести другой', 'Передать показания счётчиков']:
        return SUBMIT_READINGS
    elif text.isdigit() and user.favorites.filter(bill__value=int(text)).exists():
        return SUBMIT_READINGS
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Не понял команду. Давайте начнем сначала."
        )
        return SUBMIT_READINGS
