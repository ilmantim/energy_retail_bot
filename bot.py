import os
import django
import logging

from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
django.setup()

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,\
      ConversationHandler

from commands.start import handle_start
from commands.main_menu import fallback
from commands.main_menu import handle_main_menu
from commands.submit_readings import submit_readings
from commands.input_readings import input_readings
from commands.yes_or_no_address import yes_or_no_address
from commands.get_meter_info import get_meter_info
from commands.get_contact_info import get_contact_info
from commands.create_favorite_bill import create_favorite_bill
from commands.remove_favorite_bill import remove_favorite_bill


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
logger = logging.getLogger(__name__)


MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO,\
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)


def main() -> None:
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handle_start)],
        states={
            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command,
                                       handle_main_menu)],
            SUBMIT_READINGS: [MessageHandler(Filters.text & ~Filters.command,
                                             submit_readings)],
            INPUT_READINGS: [MessageHandler(Filters.text & ~Filters.command,
                                           input_readings)],
            YES_OR_NO_ADDRESS: [MessageHandler(Filters.text & ~Filters.command,
                                               yes_or_no_address)],
            METER_INFO: [MessageHandler(Filters.text & ~Filters.command,
                                        get_meter_info)],
            CONTACT_INFO: [MessageHandler(Filters.text & ~Filters.command,
                                          get_contact_info)],
            CREATE_FAVORITE_BILL: [MessageHandler(Filters.text & ~Filters.command,
                                             create_favorite_bill)],
            REMOVE_FAVORITE_BILLS: [MessageHandler(Filters.text & ~Filters.command,
                                           remove_favorite_bill)],   
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