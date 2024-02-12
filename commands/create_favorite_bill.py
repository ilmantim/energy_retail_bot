import logging

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from commands.before_input_readings import before_input_readings
from retail.models import Bill, Customer, Favorite
from keyboard import go_to_main_menu_keyboard


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS, BEFORE_INPUT_READINGS = range(9)


def create_favorite_bill(update: Update, context: CallbackContext) -> int:
    logger.info("create_favorite_bill")

    text = update.message.text.lower()
    bill_here = Bill.objects.get(value=int(context.user_data['bill_num']))
    user_here = Customer.objects.get(chat_id=int(context.user_data['chat_id']))

    if text == 'да':
        bill_here.customers.add(user_here)
        Favorite.objects.create(customer=user_here, bill=bill_here, is_favorite=True)

    if text == 'нет':
        bill_here.customers.add(user_here)

    if text in ['да', 'нет']:
        if context.user_data['prev_step'] == 'submit':
            devices_here = bill_here.devices.all()
            rates_ids = [rate.id for device in devices_here for rate in device.rates.all()]
            context.user_data['rates_ids'] = rates_ids
            context.user_data['non_deletable_rates_ids'] = rates_ids.copy()
            context.user_data['prev_step'] = 'fav'
            return before_input_readings(update, context)
        elif context.user_data['prev_step'] == 'meter':
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
                                 #f'  - {rate_here.title}:{rate_here_cost} ₽\n'
                                 f'-----------------------------------\n'
                                 #######ЭТОТ ТУТ НЕ НУЖНО, ОТСАВИЛ, ЧТОБЫ НЕ СЛОМАТЬ КОД#########
                                 f'Номер и тип ПУ: {number_and_type_pu_str}\n'
                                 f'Показания: {readings_str}\n'
                                 f'Дата приёма: {registration_date_str}\n'
                                 ###################################################################
                        )
                    else:
                        update.message.reply_text(
                            f'📟 Информация о приборе учета:\n'
                            f'-----------------------------------\n'
                            f'- Лицевой счет: {bill_here.value}\n'
                            f'- Прибор учета: {device_title} - {modification} (№{serial_number})\n'
                            f'- Номер счетчика: {serial_number}\n'
                            f'- Величина тарифа: \n'
                            #f'  - {rate_here.title}:{rate_here_cost} ₽\n'
                            f'-----------------------------------\n'
                            #######ЭТОТ ТУТ НЕ НУЖНО, ОТСАВИЛ, ЧТОБЫ НЕ СЛОМАТЬ КОД#########
                            f'Номер и тип ПУ: {number_and_type_pu_str}\n'
                            f'Показания: {readings_str}\n'
                            f'Дата приёма: {registration_date_str}\n',
                            ###################################################################
                            reply_markup=go_to_main_menu_keyboard()
                        )
                        return ConversationHandler.END
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Не понял команду. Давайте попробуем снова.'
        )
        if context.user_data['prev_step'] == 'submit':
            return SUBMIT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            return METER_INFO
