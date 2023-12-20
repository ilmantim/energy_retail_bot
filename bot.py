import os
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler, CallbackQueryHandler
from retail.models import Mro, Bill, Customer, Favorite
from django.utils import timezone
from datetime import datetime
from keyboard import yes_or_no_keyboard, yes_and_no_keyboard, \
    go_to_main_menu_keyboard, main_menu_keyboard, \
    submit_readnigs_and_get_meter_keyboard, \
    submit_readnigs_and_get_meter_with_bills_keyboard, \
    show_bills_keyboard, delete_bills_keyboard, \
    choose_MRO_keyboard, \
    choose_address_keyboard
from messages import HELLO
from dictionary import cheboksarskoe_mro_info, alatyrskoe_mro_info, \
    batyrevo_mro_info, \
    kanashskoe_mro_info, novocheboksarskoe_mro_info, civilskoe_mro_info, \
    shumerlinskoe_mro_info, yadrinskoe_mro_info, upravlenie_info

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS, ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(
    8)


def handle_start(update: Update, context: CallbackContext) -> int:
    """
    TODO: привязку к id пользователя ( бот же должаен помнить счета конкретного юзера)

    """

    if context.user_data.get('has_started', True):
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        context.user_data['chat_id'] = user.chat_id
        if user.favorites.count() > 0:
            context.user_data['bills_count'] = user.favorites.count()
            bills = True
        else:
            bills = False
        update.message.reply_text("Выберите раздел",
                                  reply_markup=main_menu_keyboard(bills))
    else:

        context.user_data['has_started'] = True
        update.message.reply_text(HELLO)

        update.message.reply_text(
            "Выберите раздел",
            reply_markup=main_menu_keyboard()
        )
    return MAIN_MENU


def manage_delete(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text.isdigit() and context.user_data['bills_count'] > 0:
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        user.bills.get(value=int(text)).delete()
        context.user_data['bills_count'] = user.favorites.count()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Личный счет удален из вашего списка.'
        )
        if user.favorites.count() > 0:
            bills = True
        else:
            bills = False
        update.message.reply_text("Выберите раздел",
                                  reply_markup=main_menu_keyboard(bills))
        return MAIN_MENU
    elif text == 'Назад':
        update.message.reply_text(
            "Выберите нужный пункт снизу.",
            reply_markup=show_bills_keyboard()
        )
        return MANAGE_DELETE
    elif text == 'Главное меню':
        return handle_start(update, context)
    elif text == "Удалить лицевой счёт":
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        user_bills = [str(bill.value) for bill in user.bills.all()]
        update.message.reply_text(
            "Выберите лицевой счёт, который Вы хотите удалить.",
            reply_markup=delete_bills_keyboard(user_bills)
        )
        return MANAGE_DELETE


def handle_main_menu(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logger.info("Главное меню")

    if text == "Мои лицевые счета" and context.user_data['bills_count']:
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        user_bills = [str(bill.value) for bill in user.bills.all()]
        all_bills = '\n'.join(user_bills)
        message = 'Ваши лицевые счета:\n' + all_bills
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
        update.message.reply_text(
            "Выберите нужный пункт снизу.",
            reply_markup=show_bills_keyboard()
        )
        return MANAGE_DELETE
    if text == "Передать показания счётчиков":
        return submit_readings(update, context)
    elif text == "Приборы учёта":
        return get_meter_info(update, context)
    elif text == "Контакты и режим работы":
        return get_contact_info(update, context)
    elif text == "В главное меню":
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        if user.favorites.count() > 0:
            context.user_data['bills_count'] = user.favorites.count()
            bills = True
        else:
            bills = False
        update.message.reply_text("Выберите раздел",
                                  reply_markup=main_menu_keyboard(bills))
        return MAIN_MENU
    else:
        update.message.reply_text("Не понял команду. Давайте начнем сначала.",
                                  reply_markup=main_menu_keyboard())
        return MAIN_MENU


def submit_readings(update: Update, context: CallbackContext) -> int:
    """
    TODO:
        
        -  Реализовать сценарий после ответа боту на date.message.reply_text("Введите лицевой счёт", reply_markup=submit_readnigs_and_get_meter_keyboard())

           После ввода лицевого счета сделать так, чтобы был уточняющий вопрос "Тот ли это адрес?"

            if "ДА" bot ask "Вы хотите добавить этот лицевой счёт в избранное?"
                if "ДА" ["Мои лицевые счета"] ###### добавляются в стартовую клавиатуру (как этот номер добавить в кнопку?) ###### -----------> написать def get_my_bills()
                                       and
                             bot reply:  "Лицевой счет: 100399652\n"
                                         "Номер и тип ПУ: счётчик №06485054 на электроснабжение в подъезде\n"
                                         "Показания: 21780\n"
                                         "Дата приёма: 17.11.2023\n"
                                         "Введите новые показания:
                                                                    if показания отправлены бот reply    "Ваш расход составил (разница предыдущих и отправленных показаний)"
                                                                                                          "Показания сохранены"

                                                                                                          return в главное меню

                elif "НЕТ" 
                             bot reply:  "Лицевой счет: 100399652\n"
                                         "Номер и тип ПУ: счётчик №06485054 на электроснабжение в подъезде\n"
                                         "Показания: 21780\n"
                                         "Дата приёма: 17.11.2023\n"
                                         "Введите новые показания:
                                                                     if показания отправлены бот reply    "Ваш расход составил (разница предыдущих и отправленных показаний)"
                                                                                                           "Показания сохранены"

                                                                                                           return в главное меню

 
           ###### elif "Нет" ("Тот ли это адрес?") bot reply  "Проверьте правильность введения номера лицевого счета.\n"
           ######                                             "Возможно, по данному адресу приборы учёта отсутствуют или закончился срок поверки.\n"
           ######                                             "Для уточнения информации обратитесь к специалисту контакт-центра"
           ######
           ######                                              return в главное меню
           ######

        - Реализовать передачу данных на сервер и запрос данных с сервера

        ("Данные берутся из нашей основной БД через веб-эндпоинт. Шлешь джейсон с запросом, получаешь с ответом." (c))
                

    """

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


def fill_readings(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text == "В главное меню":
        return handle_start(update, context)
    elif text.isdigit():
        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        bill_here = user_here.bills.get(
            value=int(context.user_data['bill_num']))
        if bill_here.readings:
            readings_1 = bill_here.readings
            readings_2 = int(text)
            subtraction = readings_2 - readings_1
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Ваш расход составил {subtraction} квт*ч'
            )
        bill_here.readings = int(text)
        bill_here.registration_date = timezone.now()
        bill_here.save()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Показания сохранены.'
        )
        return handle_start(update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='ты где то зафейлил'
        )


def yes_or_no_address(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text.lower() == 'нет':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Проверьте правильность введения номера лицевого счета.\n"
                 "Возможно, по данному адресу приборы учёта отсутствуют или закончился срок поверки.\n"
                 "Для уточнения информации обратитесь к специалисту контакт-центра"
        )
        return handle_start(update, context)
    elif text.lower() == 'да':
        update.message.reply_text(
            "Вы хотите добавить этот лицевой счёт в избранное?",
            reply_markup=yes_or_no_keyboard()
        )
        return ADD_TO_FAVORITE
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Это сообщение вы видите, если не ответили да/нет'
        )
        if context.user_data['prev_step'] == 'submit':
            return SUBMIT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            return METER_INFO
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='ты где то зафейлил'
            )


def add_to_favorite(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    bill_here = Bill.objects.get(value=int(context.user_data['bill_num']))
    if text.lower() == 'да':
        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        bill_here.customers.add(user_here)
        Favorite.objects.create(
            customer=user_here,
            bill=bill_here,
            is_favorite=True
        )
        message = (
            f'Лицевой счет: {bill_here.value}\n'
            f'Номер и тип ПУ: {bill_here.number_and_type_pu}\n'
            f'Показания: {bill_here.readings} квт*ч\n'
            f'Дата приёма: {bill_here.registration_date}\n'
        )
        if context.user_data['prev_step'] == 'submit':
            message += 'Введите новые показания:'
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return FILL_READINGS
        elif context.user_data['prev_step'] == 'meter':
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return METER_INFO
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='ты где то зафейлил'
            )
    elif text.lower() == 'нет':
        user_here = Customer.objects.get(
            chat_id=int(context.user_data['chat_id']))
        bill_here.customers.add(user_here)
        message = (
            f'Лицевой счет: {bill_here.value}\n'
            f'Номер и тип ПУ: {bill_here.number_and_type_pu}\n'
            f'Показания: {bill_here.readings} квт*ч\n'
            f'Дата приёма: {bill_here.registration_date}\n'
        )
        if context.user_data['prev_step'] == 'submit':
            message += 'Введите новые показания:'
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return FILL_READINGS
        elif context.user_data['prev_step'] == 'meter':
            update.message.reply_text(
                message,
                reply_markup=go_to_main_menu_keyboard()
            )
            return METER_INFO
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='ты где то зафейлил'
            )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Это сообщение вы видите, если не ответили да/нет'
        )
        if context.user_data['prev_step'] == 'submit':
            return SUBMIT_READINGS
        elif context.user_data['prev_step'] == 'meter':
            return METER_INFO
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='ты где то зафейлил'
            )


def get_meter_info(update: Update, context: CallbackContext) -> int:
    """"
     Аналогичная submit_readings 
                                  только if  отправлени лицевой счет:
                                                         bot reply "Лицевой счёт %000000% успешно найден"
                                                                    
                                                                    "Лицевой счет: 100399652\n"
                                                                    "Номер и тип ПУ: счётчик №06485054 на электроснабжение в подъезде\n"
                                                                    "Показания: 21780\n"
                                                                    "Дата приёма: 17.11.2023\n"
                                    


    """
    logger.info("Приборы учёта")
    bills = Bill.objects.all()
    text = update.message.text
    user, is_found = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id)
    context.user_data['chat_id'] = user.chat_id
    if text.isdigit() and bills.filter(value=int(text)).exists():
        context.user_data['bill_num'] = text
        bill_here = bills.get(value=int(text))
        user_bills = user.bills.all()
        if user_bills.filter(value=bill_here.value).exists():
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
    if user_here.bills.count() > 0 and not text == 'Ввести другой':
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


def get_contact_info(update: Update, context: CallbackContext) -> int:
    global prev_department
    logger.info("Контакты и режим работы")
    text = update.message.text
    if text.isdigit() and prev_department:
        department_here = Mro.objects.get(name=prev_department)
        addresses = department_here.addresses.all()
        address_here = addresses.get(num=int(text))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=address_here.name
        )
        return handle_start(update, context)
    elif text == "Главное меню":
        logger.info("Returning to main menu")
        return handle_start(update, context)
    elif Mro.objects.filter(name=text).exists():
        department = Mro.objects.get(name=text)
        if department.addresses.count() > 0:
            addresses = [str(i + 1) for i in
                         range(department.addresses.count())]

            prev_department = department.name
            update.message.reply_text(
                department.general,
                reply_markup=choose_address_keyboard(addresses)
            )
            update.message.reply_text(
                "Выберите номер удобного для Вас МРО в меню снизу")
            return CONTACT_INFO
        else:
            update.message.reply_text(
                department.general,
                reply_markup=main_menu_keyboard()
            )
            return handle_start(update, context)
    else:
        update.message.reply_text(
            "Выберите МРО",
            reply_markup=choose_MRO_keyboard()
        )
        return CONTACT_INFO


def fallback(update: Update, context: CallbackContext) -> int:
    logger.warning("Неизвестная команда")
    update.message.reply_text("Не понял команду. Давайте начнем сначала.",
                              reply_markup=main_menu_keyboard())
    return MAIN_MENU


def main() -> None:
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handle_start)],
        states={
            MANAGE_DELETE: [MessageHandler(Filters.text & ~Filters.command,
                                           manage_delete)],
            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command,
                                       handle_main_menu)],
            SUBMIT_READINGS: [MessageHandler(Filters.text & ~Filters.command,
                                             submit_readings)],
            FILL_READINGS: [MessageHandler(Filters.text & ~Filters.command,
                                           fill_readings)],
            YES_OR_NO_ADDRESS: [MessageHandler(Filters.text & ~Filters.command,
                                               yes_or_no_address)],
            ADD_TO_FAVORITE: [MessageHandler(Filters.text & ~Filters.command,
                                             add_to_favorite)],
            METER_INFO: [MessageHandler(Filters.text & ~Filters.command,
                                        get_meter_info)],
            CONTACT_INFO: [MessageHandler(Filters.text & ~Filters.command,
                                          get_contact_info)],
        },
        fallbacks=[
            CommandHandler('start', handle_start),
            MessageHandler(Filters.text, fallback)
        ]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logger.info("Бот запущен")
    main()
