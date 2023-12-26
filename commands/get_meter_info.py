import requests
import logging
import datetime
from telegram import Update
from telegram.ext import CallbackContext
from django.utils import timezone

from retail.models import Bill, Customer, Favorite
from keyboard import yes_or_no_keyboard, go_to_main_menu_keyboard, submit_readings_and_get_meter_keyboard
from commands.start import handle_start

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot states
MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO, CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)

def get_meter_info(update: Update, context: CallbackContext) -> int:
    logger.info("Meter Info Processing")
    text = update.message.text
    user, _ = Customer.objects.get_or_create(chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id
    user_bills = Favorite.objects.filter(customer=user)

    if text == "В главное меню":
        return handle_start(update, context)
    elif text == "Как узнать лицевой счёт":
        update.message.reply_text(
            "Лицевой счёт указан в верхней части квитанции (извещение) рядом с Вашей фамилией.\n"
            "Введите лицевой счёт", reply_markup=submit_readings_and_get_meter_keyboard())
        return METER_INFO

    try:
        bill_here = process_meter_info_text(text, user_bills, context, update)
        if bill_here:
            if user_bills.filter(bill__value=bill_here.value).exists():
                display_bill_info(update, bill_here)
                return MAIN_MENU
            else:
                prompt_for_address_confirmation(update, bill_here)
                return YES_OR_NO_ADDRESS
    except Bill.DoesNotExist:
        send_error_message(update, context)
        return handle_start(update, context)

    user_here = Customer.objects.get(chat_id=int(context.user_data['chat_id']))
    if user_here.favorites.count() > 0 and text != 'Ввести другой':
        display_favorite_bills(update, user_here)
        return SUBMIT_READINGS
    else:
        prompt_for_bill_number(update)
        return METER_INFO

def process_meter_info_text(text, user_bills, context, update):
    if not text.isdigit():
        return None

    bill_id_response = get_bill_id(text)
    if not bill_id_response or "id_PA" not in bill_id_response[0]:
        send_bill_not_found_message(update, text)
        return None

    bill_info = get_bill_info(bill_id_response[0]["id_PA"])
    if not bill_info or text not in bill_info.values():
        send_bill_not_found_message(update, text)
        return None

    bill_here, _ = Bill.objects.get_or_create(value=int(text))
    update_bill_info(bill_info, bill_here)
    return bill_here

def get_bill_id(text):
    url_for_id = f"https://lk-api-dev.backspark.ru/api/v0/cabinet/terminal/getAccounts/{text}"
    return get_api_response(url_for_id)

def get_bill_info(bill_id):
    url_for_bill = f"https://lk-api-dev.backspark.ru/api/v0/cabinet/terminal/getAccountInfo/{bill_id}"
    return get_api_response(url_for_bill)

def get_api_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f'Error in API request: {e}')
        return None

def update_bill_info(bill_info, bill):
    # Assuming bill_info contains a dictionary with relevant fields
    # Update the bill object with new info from bill_info

    # Example of updating properties - adjust these according to your actual model fields
    bill.number_and_type_pu = f'счётчик {bill_info["core_devices"][0]["serial_number"]} на электроснабжение в подъезде'
    readings = bill_info["core_devices"][0]["rates"][0]["current_month_reading_value"]
    if readings:
        bill.readings = int(round(float(readings)))

    date = bill_info["core_devices"][0]["rates"][0]["current_month_reading_date"]
    if date:
        # Splitting the date string and removing milliseconds
        date = date.split('.')[0]
        moscow_timezone = timezone.get_fixed_timezone(180)
        bill.registration_date = datetime.datetime.strptime(
            date, "%Y-%m-%dT%H:%M:%S"
        ).replace(tzinfo=datetime.timezone.utc).astimezone(tz=moscow_timezone)

    bill.address = (
        f'{bill_info["core_devices"][0]["locality"]} '
        f'{bill_info["core_devices"][0]["street"]} '
        f'{bill_info["core_devices"][0]["type_house"]} '
        f'{bill_info["core_devices"][0]["house"]} '
        f'{bill_info["core_devices"][0]["condos_types"]} '
        f'{bill_info["core_devices"][0]["condos_number"]}'
    )

    bill.save()
    return bill


def send_error_message(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Не понял команду. Давайте начнем сначала.")

def send_bill_not_found_message(update, bill_number):
    update.message.reply_text(
        f"Не удалось найти счет {bill_number}.\n"
        "Проверьте правильность введения номера лицевого счета.\n"
        "Возможно, по данному адресу приборы учёта отсутствуют или закончился срок поверки.\n"
        "Для уточнения информации обратитесь к специалисту контакт-центра")
    return handle_start(update, context)

def display_bill_info(update, bill):
    update.message.reply_text(
        f'Лицевой счет: {bill.value}\n'
        f'Номер и тип ПУ: {bill.number_and_type_pu}\n'
        f'Показания: {bill.readings} квт*ч\n'
        f'Дата приёма: {bill.registration_date.date().strftime("%d-%m-%Y")}\n',
        reply_markup=go_to_main_menu_keyboard())

def prompt_for_address_confirmation(update, bill):
    message = f'Адрес объекта - {bill.address}?'
    update.message.reply_text(message, reply_markup=yes_or_no_keyboard())

def display_favorite_bills(update, user):
    bills = user.favorites.all()
    info = [[fav_bill.bill.value] for fav_bill in bills]
    update.message.reply_text("Выберите нужный пункт в меню снизу.",
                              reply_markup=submit_readings_and_get_meter_keyboard(info))

def prompt_for_bill_number(update):
    update.message.reply_text("Введите лицевой счет", reply_markup=submit_readings_and_get_meter_keyboard(None))