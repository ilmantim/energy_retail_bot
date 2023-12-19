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
    shumerlinskoe_mro_info, yadrinskoe_mro_info, upravlenie_info


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

