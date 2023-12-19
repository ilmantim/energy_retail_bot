import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,\
    CallbackContext,ConversationHandler
import logging
from datetime import datetime
from keyboard import yes_or_no_keyboard, yes_and_no_keyboard,\
    go_to_main_menu_keyboard, main_menu_keyboard,\
    main_menu_with_bills_keyboard, submit_readnigs_and_get_meter_keyboard,\
    submit_readnigs_and_get_meter_with_bills_keyboard,\
    show_bills_keyboard, delete_bills_keyboard,\
    choose_MRO_keyboard, choose_MRO_1_2_keyboard,\
    choose_MRO_1_2_3_keyboard, choose_MRO_1_2_3_4_keyboard
from messages import HELLO
from dictionary import cheboksarskoe_mro_info, alatyrskoe_mro_info, batyrevo_mro_info, \
    kanashskoe_mro_info, novocheboksarskoe_mro_info, civilskoe_mro_info, \
    shumerlinskoe_mro_info, yadrinskoe_mro_info, upravlenie_info,\
    keyboard_mapping, mro_mapping


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, METER_INFO, CONTACT_INFO, DETAILED_INFO  = range(5)


def handle_start(update: Update, context: CallbackContext) -> int:
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
    logger.info("Контакты и режим работы")
    text = update.message.text

    if text == "Главное меню":
        logger.info("Returning to main menu")
        return handle_start(update, context)

    mro_info = mro_mapping.get(text)
    if mro_info:
        keyboard_func = keyboard_mapping.get(text, choose_MRO_keyboard)
        update.message.reply_text(mro_info["general"], reply_markup=keyboard_func())

        context.user_data['selected_mro_info'] = mro_info.get("detailed", {})
        
        if context.user_data['selected_mro_info']:
            update.message.reply_text("Выберите номер удобного для Вас МРО в меню снизу")
            return DETAILED_INFO
        else:
            update.message.reply_text("Выберите раздел")
            return MAIN_MENU  
    else:
        update.message.reply_text("Выберите МРО", reply_markup=choose_MRO_keyboard())
        return CONTACT_INFO


def get_detailed_info(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    detailed_info = context.user_data.get('selected_mro_info')

    if detailed_info and text.isdigit():
        mro_detailed_info = detailed_info.get(int(text))
        if mro_detailed_info:
            update.message.reply_text(mro_detailed_info, reply_markup=main_menu_keyboard())
            update.message.reply_text("Выберите раздел")
            return MAIN_MENU
        else:
            update.message.reply_text("Информация по выбранному номеру отсутствует.", reply_markup=main_menu_keyboard())
            return MAIN_MENU
   

    
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
            DETAILED_INFO: [MessageHandler(Filters.text & ~Filters.command, get_detailed_info)]
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