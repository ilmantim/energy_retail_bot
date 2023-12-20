import os
import django
import logging

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,\
      ConversationHandler

from commands.start import handle_start
from commands.main_menu import fallback
from commands.main_menu import handle_main_menu
from commands.submit_readings import submit_readings
from commands.get_meter_info import get_meter_info
from commands.get_contact_info import get_contact_info

from commands.manage_delete import manage_delete

from commands.fill_readings import fill_readings
from commands.yes_or_no_address import yes_or_no_address
from commands.add_to_favorite import add_to_favorite

from commands.main_menu import fallback


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

MANAGE_DELETE, MAIN_MENU, SUBMIT_READINGS, FILL_READINGS, YES_OR_NO_ADDRESS,\
    ADD_TO_FAVORITE, METER_INFO, CONTACT_INFO = range(8)


def main() -> None:
    load_dotenv()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energy_retail_bot.settings')
    django.setup()

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