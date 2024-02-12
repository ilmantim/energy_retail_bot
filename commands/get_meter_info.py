import logging

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from commands.submit_readings import retrieve_bill_info
from retail.models import Bill, Customer, Favorite, Rate, Device

from keyboard import yes_or_no_keyboard, go_to_main_menu_keyboard, submit_readings_and_get_meter_keyboard
from commands.start import handle_start
from django.utils import timezone


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS, BEFORE_INPUT_READINGS = range(9)

MAIN_MENU_COMMAND = "В главное меню"
GET_BILL_INFO_COMMAND = "Как узнать лицевой счёт"
MOSCOW_TIMEZONE_OFFSET = 180


def get_meter_info(update: Update, context: CallbackContext) -> int:
    logger.info("Приборы учёта")
    text = update.message.text

    if text == MAIN_MENU_COMMAND:
        return handle_main_menu(update, context)
    elif text == GET_BILL_INFO_COMMAND:
        return handle_get_bill_info(update, context)
    else:
        return process_meter_info(update, context)


def handle_main_menu(update: Update, context: CallbackContext):
    context.user_data['prev_step'] = 'main'
    return handle_start(update, context)


def handle_get_bill_info(update: Update, context: CallbackContext):
    context.user_data['prev_step'] = 'get_bill'
    update.message.reply_text(
        "Лицевой счёт указан в верхней части квитанции (извещение) "
        "рядом с Вашей фамилией \nВведите лицевой счет:",
        reply_markup=submit_readings_and_get_meter_keyboard()
    )
    return METER_INFO


def process_meter_info(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    chat_id = update.effective_chat.id
    context.user_data['chat_id'] = chat_id
    user, _ = Customer.objects.get_or_create(chat_id=chat_id)
    bill_id = str(text)
    bills = Bill.objects.all()
    user_bills = Favorite.objects.filter(customer=user)
    try:
        if ((text.isdigit() and not context.user_data[
                                        'prev_step'] == 'choose') or (
                text.isdigit() and user_bills.filter(
                bill__value=bills.get(value=int(text)).value).exists())):
            response_bill = retrieve_bill_info(bill_id)
            if response_bill and text in response_bill.values():
                context.user_data['bill_num'] = text
                bill_here, created = Bill.objects.get_or_create(
                    value=int(text))
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Счет успешно найден."
                )
                for device_num in range(len(response_bill["core_devices"])):
                    device_here, created = Device.objects.get_or_create(
                        device_title=f'{response_bill["core_devices"][device_num]["device_title"]}',
                        modification=f'{response_bill["core_devices"][device_num]["modification"]}',
                        number_and_type_pu=f'{response_bill["core_devices"][device_num]["serial_number"]}',
                        serial_number=f'{response_bill["core_devices"][device_num]["serial_number"]}',
                        id_device=response_bill["core_devices"][device_num][
                            "id_meter"],
                        bill=bill_here
                    )

                    for rate_num in range(len(
                            response_bill["core_devices"][device_num][
                                "rates"])):
                        rate_here, created = Rate.objects.update_or_create(
                            title=
                            response_bill["core_devices"][device_num]["rates"][
                                rate_num]["title"],
                            id_tariff=
                            response_bill["core_devices"][device_num]["rates"][
                                rate_num]["id_tariff"],
                            device=device_here,
                            defaults={
                                'id_indication':
                                    response_bill["core_devices"][device_num][
                                        "rates"][rate_num]["id_indication"]
                            }
                        )
                        context.user_data['rate'] = rate_here.id
                        readings = \
                            response_bill["core_devices"][device_num]["rates"][
                                rate_num]["current_month_reading_value"]
                        if readings:
                            rate_here.readings = int(
                                round(float(readings)))
                        else:
                            rate_here.readings = None

                        date = \
                        response_bill["core_devices"][device_num]["rates"][
                            rate_num]["current_month_reading_date"]
                        if date:
                            moscow_timezone = timezone.get_fixed_timezone(180)
                            try:
                                rate_here.registration_date = timezone.datetime.strptime(
                                    date,
                                    "%Y-%m-%dT%H:%M:%S.%fZ"
                                ).astimezone(tz=moscow_timezone)
                            except ValueError:
                                rate_here.registration_date = timezone.datetime.strptime(
                                    date,
                                    "%Y-%m-%dT%H:%M:%SZ"
                                ).astimezone(tz=moscow_timezone)
                        else:
                            rate_here.registration_date = None
                        rate_here.save()
                    device_here.address = (
                        f'{response_bill["core_devices"][device_num]["type_locality"]}. '
                        f'{response_bill["core_devices"][device_num]["locality"]} '
                        f'{response_bill["core_devices"][device_num]["type_street"]}. '
                        f'{response_bill["core_devices"][device_num]["street"]} '
                        f'{response_bill["core_devices"][device_num]["type_house"]} '
                        f'{response_bill["core_devices"][device_num]["house"]} '
                        f'{response_bill["core_devices"][device_num]["type_building"]} '
                        f'{response_bill["core_devices"][device_num]["building"]} '
                        f'{response_bill["core_devices"][device_num]["condos_types"]} '
                        f'{response_bill["core_devices"][device_num]["condos_number"]} ')
                    device_here.save()
                bill_here.save()
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Проверьте правильность введения номера лицевого счета.\n"
                         "Возможно, по данному адресу приборы учёта отсутствуют или закончился срок поверки.\n"
                         "Для уточнения информации обратитесь к специалисту контакт-центра",
                )
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Введите лицевой счёт",
                    reply_markup=submit_readings_and_get_meter_keyboard()
                )
                return METER_INFO

            user_bills = Favorite.objects.filter(customer=user)
            if user_bills.filter(bill__value=bill_here.value).exists():
                devices = bill_here.devices.all()
                for device_here in devices:
                    rates = device_here.rates.all()
                    for rate_here in rates:
                        registration_date_str = (
                            rate_here.registration_date.date().strftime("%d.%m.%Y")
                            if rate_here.registration_date else "Дата не указана"
                        )
                        readings_str = str(
                            rate_here.readings) + ' квт*ч' if rate_here.readings is not None else "Показания не указаны"
                        number_and_type_pu_str = device_here.number_and_type_pu if device_here.number_and_type_pu else "Номер и тип ПУ не указаны"
                        device_title=device_here.device_title
                        modification=device_here.modification
                        serial_number=device_here.serial_number

                        if not device_here == bill_here.devices.last() or not rate_here == device_here.rates.last():
                            context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=f'📟 Информация о приборе учета:\n'
                                     f'-----------------------------------\n'
                                     f'- Лицевой счет: {bill_here.value}\n'
                                     f'- Прибор учета: {device_title} - {modification} (№{serial_number})\n'
                                     f'- Номер счетчика: {serial_number}\n'
                                     f'- Величина тарифа: \n'
                                     f'  - {title}:{cost} ₽\n'
                                     f'-----------------------------------\n'
                                     f'Номер и тип ПУ: {number_and_type_pu_str}\n'
                                     f'Показания: {readings_str}\n'
                                     f'Дата приёма: {registration_date_str}\n'
                            )
                        else:
                            update.message.reply_text(
                                f'📟 Информация о приборе учета:\n'
                                f'-----------------------------------\n'
                                f'- Лицевой счет: {bill_here.value}\n'
                                f'- Прибор учета: {device_title} - {modification} (№{serial_number})\n'
                                f'Номер и тип ПУ: {number_and_type_pu_str}\n'
                                f'- Номер счетчика: {serial_number}\n'
                                f'Показания: {readings_str}\n'
                                f'Дата приёма: {registration_date_str}\n'
                                f'-----------------------------------\n',
                                reply_markup=go_to_main_menu_keyboard()
                            )
                            return ConversationHandler.END
            else:
                context.user_data['prev_step'] = 'meter'
                device_here = bill_here.devices.first()
                message = f'Адрес объекта - {device_here.address}?'
                update.message.reply_text(message,
                                          reply_markup=yes_or_no_keyboard())
                return YES_OR_NO_ADDRESS

    except Exception as e:
        logger.info(f'Exception occurred:{e}')

    user_here = Customer.objects.get(
        chat_id=int(context.user_data['chat_id']))
    if user_here.favorites.count() > 0 and not text == 'Ввести другой':
        bills_here = user_here.favorites.all()
        info = [[fav_bill.bill.value] for fav_bill in bills_here]
        update.message.reply_text("Выберите нужный пункт в меню снизу.",
                                  reply_markup=submit_readings_and_get_meter_keyboard(
                                      info))
        context.user_data['prev_step'] = 'choose'
        return digit_checker(update, context)
    else:
        info = None
        context.user_data['prev_step'] = 'meters'
        update.message.reply_text("Введите лицевой счёт",
                                  reply_markup=submit_readings_and_get_meter_keyboard(
                                      info))
        return METER_INFO


def digit_checker(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user = Customer.objects.get(chat_id=int(context.user_data['chat_id']))
    if text in [GET_BILL_INFO_COMMAND, MAIN_MENU_COMMAND, 'Ввести другой', 'Приборы учёта']:
        return METER_INFO
    elif text.isdigit() and user.favorites.filter(bill__value=int(text)).exists():
        return METER_INFO
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Не понял команду. Давайте начнем сначала."
        )
        return METER_INFO
