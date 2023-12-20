import os
import django
import logging


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext, ConversationHandler, CallbackQueryHandler
from retail.models import Mro
from datetime import datetime
from keyboard import yes_or_no_keyboard, yes_and_no_keyboard, \
    go_to_main_menu_keyboard, main_menu_keyboard, \
    main_menu_with_bills_keyboard, submit_readnigs_and_get_meter_keyboard, \
    submit_readnigs_and_get_meter_with_bills_keyboard, \
    show_bills_keyboard, delete_bills_keyboard, \
    choose_MRO_keyboard,  \
    choose_address_keyboard
from messages import HELLO
from dictionary import cheboksarskoe_mro_info, alatyrskoe_mro_info, batyrevo_mro_info, \
    kanashskoe_mro_info, novocheboksarskoe_mro_info, civilskoe_mro_info, \
    shumerlinskoe_mro_info, yadrinskoe_mro_info, upravlenie_info


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, METER_INFO, CONTACT_INFO = range(4)


def handle_start(update: Update, context: CallbackContext) -> int:
    """
    TODO: привязку к id пользователя ( бот же должаен помнить счета конкретного юзера)

    """
    # Если бот уже запущен
    if context.user_data.get('has_started', False):
        # Бот уже запущен, не выдаём HELLO
        update.message.reply_text("Выберите раздел", reply_markup=main_menu_keyboard())
    else:
        # Первый запуск бота
        context.user_data['has_started'] = True
        update.message.reply_text(HELLO)

        update.message.reply_text(
        "Выберите раздел",
        reply_markup=main_menu_keyboard()
        )
    return MAIN_MENU


def handle_main_menu(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logger.info("Главное меню")

    if text == "Передать показания счётчиков":
        return submit_readings(update, context)
    elif text == "Приборы учёта":
        return get_meter_info(update, context)
    elif text == "Контакты и режим работы":
        return get_contact_info(update, context)
    else:
        update.message.reply_text("Не понял команду. Давайте начнем сначала.", reply_markup=main_menu_keyboard())
        return MAIN_MENU


def submit_readings(update: Update, context: CallbackContext) -> int:

    """
    TODO:
        
        -  Реализовать сценарий после ответа боту на date.message.reply_text("Введите лицевой счёт", reply_markup=submit_readnigs_and_get_meter_keyboard())

           После ввода лицевого счета сделать так, чтобы был уточняющий вопрос "Тот ли это адрес?"

            if "ДА" bot ask "Вы хотите добавить этот лицевой счёт в избранное?"
                if "ДА" ["Мои лицевые счета"] добавляются в стартовую клавиатуру (как этот номер добавить в кнопку?) -----------> написать def get_my_bills()
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

 
            elif "Нет" ("Тот ли это адрес?") bot reply  "Проверьте правильность введения номера лицевого счета.\n"
                                                        "Возможно, по данному адресу приборы учёта отсутствуют или закончился срок поверки.\n"
                                                         "Для уточнения информации обратитесь к специалисту контакт-центра"

                                                          return в главное меню


        - Реализовать передачу данных на сервер и запрос данных с сервера

        ("Данные берутся из нашей основной БД через веб-эндпоинт. Шлешь джейсон с запросом, получаешь с ответом." (c))
                

    """

    logger.info("Передать показания счётчиков")
    text = update.message.text

    if text == "В главное меню":
        return handle_start(update, context)

    elif text == "Как узнать лицевой счёт":
        update.message.reply_text("Лицевой счёт указан в верхней части квитанции (извещение) рядом с Вашей фамилией")
        update.message.reply_text("Введите лицевой счет", reply_markup=submit_readnigs_and_get_meter_keyboard())
        return SUBMIT_READINGS

    today = datetime.now()
    if 15 <= today.day <= 25:
        update.message.reply_text("Введите лицевой счёт", reply_markup=submit_readnigs_and_get_meter_keyboard())
        return SUBMIT_READINGS
    
    else:
        update.message.reply_text("Показания принимаются с 15 по 25 число каждого месяца.")
        return MAIN_MENU


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
    text = update.message.text

    if text == "В главное меню":
        return handle_start(update, context)
    elif text == "Как узнать лицевой счёт":
        update.message.reply_text("Лицевой счёт указан в верхней части квитанции (извещение) рядом с Вашей фамилией.", reply_markup=submit_readnigs_and_get_meter_keyboard())
        return METER_INFO
    else:
        update.message.reply_text("Введите лицевой счет", reply_markup=submit_readnigs_and_get_meter_keyboard())
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
            addresses = [str(i+1) for i in range(department.addresses.count())]

            prev_department = department.name
            update.message.reply_text(
                department.general,
                reply_markup=choose_address_keyboard(addresses)
            )
            update.message.reply_text("Выберите номер удобного для Вас МРО в меню снизу")
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
    update.message.reply_text("Не понял команду. Давайте начнем сначала.", reply_markup=main_menu_keyboard())
    return MAIN_MENU


def main() -> None:
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handle_start)],
        states={
            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, handle_main_menu)],
            SUBMIT_READINGS: [MessageHandler(Filters.text & ~Filters.command, submit_readings)],
            METER_INFO: [MessageHandler(Filters.text & ~Filters.command, get_meter_info)],
            CONTACT_INFO: [MessageHandler(Filters.text & ~Filters.command, get_contact_info)],
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