import logging
import requests
from datetime import datetime, timezone  # Corrected imports
from django.utils import timezone as django_timezone
from telegram import Update
from telegram.ext import CallbackContext

from retail.models import Bill, Customer, Favorite
from keyboard import yes_or_no_keyboard, go_to_main_menu_keyboard, submit_readings_and_get_meter_keyboard
from commands.start import handle_start

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO, CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)

def submit_readings(update: Update, context: CallbackContext) -> int:
    logger.info("Meter Readings Submission")
    text = update.message.text
    user, _ = Customer.objects.get_or_create(chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id

    if text == "В главное меню":
        return handle_start(update, context)
    elif text == "Как узнать лицевой счёт":
        return prompt_for_account_number(update)

    if not valid_submission_period():
        update.message.reply_text("Показания принимаются с 15 по 25 число каждого месяца.")
        return handle_start(update, context)

    try:
        return handle_reading_submission(text, update, context, user)
    except Bill.DoesNotExist:
        send_error_message(update, context)
        return handle_start(update, context)
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        logger.error(f'A connection error occurred: {e}')
        return SUBMIT_READINGS

def handle_reading_submission(text, update, context, user):
    user_bills = Favorite.objects.filter(customer=user)
    if text.isdigit():
        return process_reading_submission(text, update, context, user_bills)
    
    if user.favorites.count() > 0 and text != 'Ввести другой':
        return display_favorite_bills(update, context, user)

    return prompt_for_meter_reading(update, context)

def process_reading_submission(text, update, context, user_bills):
    response_bill = fetch_bill_info(text)
    if response_bill and text in response_bill.values():
        bill_here = update_bill_info(response_bill, text)
        return handle_found_bill(bill_here, update, context, user_bills)
    
    send_bill_not_found_message(update, text)
    return SUBMIT_READINGS

def fetch_bill_info(account_number):
    bill_id_response = get_api_response(f"https://lk-api-pp.backspark.ru/api/v0/cabinet/terminal/getAccounts/{account_number}")
    if not bill_id_response or "id_PA" not in bill_id_response[0]:
        return None

    bill_info_url = f"https://lk-api-pp.backspark.ru/api/v0/cabinet/terminal/getAccountInfo/{bill_id_response[0]['id_PA']}"
    return get_api_response(bill_info_url)

def update_bill_info(bill_info, account_number):
    bill, _ = Bill.objects.get_or_create(value=int(account_number))

    # Example of updating properties based on the bill_info structure
    bill.number_and_type_pu = f'счётчик {bill_info["core_devices"][0]["serial_number"]} на электроснабжение в подъезде'
    readings = bill_info["core_devices"][0]["rates"][0]["current_month_reading_value"]
    if readings:
        bill.readings = int(round(float(readings)))

    date = bill_info["core_devices"][0]["rates"][0]["current_month_reading_date"]
    if date:
        if date.endswith('Z'):
            date = date[:-1] + '+00:00'  # Correctly format for UTC offset

        moscow_timezone = django_timezone.get_fixed_timezone(180)
        bill.registration_date = datetime.strptime(
            date, "%Y-%m-%dT%H:%M:%S%z"  # Updated to include timezone offset parsing
        ).astimezone(tz=moscow_timezone)


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


def get_api_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f'Error in API request: {e}')
        return None

def valid_submission_period():
    today = datetime.now()
    return 15 <= today.day <= 30

def prompt_for_account_number(update):
    update.message.reply_text(
        "Лицевой счёт указан в верхней части квитанции (извещение) рядом с Вашей фамилией \nВведите лицевой счет:",
        reply_markup=submit_readings_and_get_meter_keyboard())
    return SUBMIT_READINGS

def handle_found_bill(bill, update, context, user_bills):
    if user_bills.filter(bill__value=bill.value).exists():
        # Check if each attribute is set, and provide a default value if it's None
        number_and_type_pu = bill.number_and_type_pu if bill.number_and_type_pu else "Not available"
        readings_str = str(bill.readings) if bill.readings is not None else "Not available"
        registration_date_str = (bill.registration_date.date().strftime("%Y-%m-%d")
                                 if bill.registration_date else "Not available")

        update.message.reply_text(
            f'Лицевой счет: {bill.value}\n'
            f'Номер и тип ПУ: {number_and_type_pu}\n'
            f'Показания: {readings_str} квт*ч\n'
            f'Дата приёма: {registration_date_str}\n'
            'Введите новые показания:',
            reply_markup=go_to_main_menu_keyboard()
        )
        return INPUT_READINGS
    else:
        message = f'Адрес объекта - {bill.address}?'
        update.message.reply_text(message, reply_markup=yes_or_no_keyboard())
        context.user_data['prev_step'] = 'submit'
        return YES_OR_NO_ADDRESS

def send_error_message(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Не понял команду. Давайте начнем сначала.")

def send_bill_not_found_message(update, bill_number):
    update.message.reply_text(
        f"Не удалось найти счет {bill_number}.\n"
        "Проверьте правильность введения номера лицевого счета.\n"
        "Возможно, по данному адресу приборы учёта отсутствуют или закончился срок поверки.\n"
        "Для уточнения информации обратитесь к специалисту контакт-центра")
    return handle_start(update, context)

def display_favorite_bills(update, context, user):
    bills_here = user.favorites.all()
    info = [[fav_bill.bill.value] for fav_bill in bills_here]
    update.message.reply_text("Выберите нужный пункт в меню снизу.",
                              reply_markup=submit_readings_and_get_meter_keyboard(info))
    context.user_data['prev_step'] = 'choose'
    return digit_checker(update, context)

def prompt_for_meter_reading(update, context):
    context.user_data['prev_step'] = 'enter_readings'
    update.message.reply_text("Введите лицевой счёт", reply_markup=submit_readings_and_get_meter_keyboard(None))
    return SUBMIT_READINGS

def digit_checker(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user_here = Customer.objects.get(chat_id=int(context.user_data['chat_id']))
    if text in ["Как узнать лицевой счёт", "В главное меню", 'Ввести другой', 'Передать показания счётчиков']:
        return SUBMIT_READINGS
    elif text.isdigit() and user_here.favorites.filter(bill__value=int(text)).exists():
        return SUBMIT_READINGS
    else:
        send_error_message(update, context)
        return SUBMIT_READINGS
