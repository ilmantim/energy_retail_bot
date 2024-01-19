import logging

import requests
from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Mro, Bill, Customer, Favorite, Rate
from datetime import datetime
from keyboard import yes_or_no_keyboard, \
    go_to_main_menu_keyboard, \
    submit_readnigs_and_get_meter_keyboard

from commands.start import handle_start
from database import response_1, response_2
from django.utils import timezone

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO, \
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)


def submit_readings(update: Update, context: CallbackContext) -> int:
    logger.info("Передать показания счётчиков")
    text = update.message.text
    user, is_found = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id

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
            if (text.isdigit() and not context.user_data[
                                           'prev_step'] == 'choose') or (
                    text.isdigit() and user_bills.filter(
                    bill__value=bills.get(value=int(text)).value).exists()):
                url_for_id = f"https://lk-api-dev.backspark.ru/api/v0/cabinet/terminal/getAccounts/{text}"
                response = requests.get(url_for_id)
                response.raise_for_status()
                response_id = response.json()
                if response_id and "id_PA" in response_id[0]:
                    bill_id = str(response_id[0]["id_PA"])
                    url_for_bill = f"https://lk-api-dev.backspark.ru/api/v0/cabinet/terminal/getAccountInfo/{bill_id}"
                    response = requests.get(url_for_bill)
                    response.raise_for_status()
                    response_bill = response.json()
                    if text in response_bill.values():
                        context.user_data['bill_num'] = text
                        bill_here, is_found = Bill.objects.get_or_create(
                            value=int(text))
                        context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text="Счет успешно найден."
                        )

                        bill_here.number_and_type_pu = f'счётчик {response_bill["core_devices"][0]["serial_number"]} на электроснабжение в подъезде'
                        bill_here.id_device = response_bill["core_devices"][0][
                            "id_meter"]

                        for rate_num in range(len(
                                response_bill["core_devices"][0]["rates"])):
                            rate_here, created = Rate.objects.get_or_create(
                                id_tariff=
                                response_bill["core_devices"][0]["rates"][
                                    rate_num]["id_tariff"],
                                id_indication=
                                response_bill["core_devices"][0]["rates"][0][
                                    "id_indication"],
                                bill=bill_here
                            )
                            context.user_data['rate'] = rate_here.id
                            readings = \
                                response_bill["core_devices"][0]["rates"][
                                    rate_num]["current_month_reading_value"]
                            if readings:
                                rate_here.readings = int(
                                    round(float(readings)))
                            else:
                                rate_here.readings = None

                            date = response_bill["core_devices"][0]["rates"][
                                rate_num]["current_month_reading_date"]
                            if date:
                                moscow_timezone = timezone.get_fixed_timezone(
                                    180)
                                rate_here.registration_date = timezone.datetime.strptime(
                                    date,
                                    "%Y-%m-%dT%H:%M:%S.%fZ"
                                ).astimezone(tz=moscow_timezone)
                            else:
                                rate_here.registration_date = None
                            rate_here.save()
                        bill_here.address = (
                            f'{response_bill["core_devices"][0]["locality"]} '
                            f'{response_bill["core_devices"][0]["street"]} '
                            f'{response_bill["core_devices"][0]["type_house"]} '
                            f'{response_bill["core_devices"][0]["house"]} '
                            f'{response_bill["core_devices"][0]["condos_types"]} '
                            f'{response_bill["core_devices"][0]["condos_number"]} ')
                        bill_here.save()
                    else:
                        context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text="Не удалось найти счет."
                        )
                        return SUBMIT_READINGS
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Не удалось найти счет."
                    )
                    return SUBMIT_READINGS

                if user_bills.filter(bill__value=bill_here.value).exists():

                    registration_date_str = (
                        bill_here.registration_date.date().strftime("%Y-%m-%d")
                        if bill_here.registration_date else "Дата не указана"
                    )
                    readings_str = str(
                        bill_here.readings) + ' квт*ч' if readings is not None else "Показания не указаны"
                    number_and_type_pu_str = bill_here.number_and_type_pu if date else "Номер и тип ПУ не указаны"

                    update.message.reply_text(
                        f'Лицевой счет: {bill_here.value}\n'
                        f'Номер и тип ПУ: {number_and_type_pu_str}\n'
                        f'Показания: {readings_str}\n'
                        f'Дата приёма: {registration_date_str}\n'
                        'Введите новые показания:',
                        reply_markup=go_to_main_menu_keyboard()
                    )
                    return INPUT_READINGS

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

        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        if user_here.favorites.count() > 0 and not text == 'Ввести другой':
            bills_here = user_here.favorites.all()
            info = [[fav_bill.bill.value] for fav_bill in bills_here]
            update.message.reply_text("Выберите нужный пункт в меню снизу.",
                                      reply_markup=submit_readnigs_and_get_meter_keyboard(
                                          info))
            context.user_data['prev_step'] = 'choose'
            return digit_checker(update, context)
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


def digit_checker(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user_here = Customer.objects.get(
        chat_id=int(context.user_data['chat_id']))
    if text in ["Как узнать лицевой счёт", "В главное меню", 'Ввести другой',
                'Передать показания счётчиков']:
        return SUBMIT_READINGS
    elif text.isdigit() and user_here.favorites.filter(
            bill__value=int(text)).exists():
        return SUBMIT_READINGS
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не понял команду. Давайте начнем сначала."
        )
        return SUBMIT_READINGS