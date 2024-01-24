import logging

from telegram import Update
from telegram.ext import CallbackContext

from commands.start import handle_start
from commands.submit_readings import submit_readings
from commands.get_meter_info import get_meter_info
from commands.get_contact_info import get_contact_info

from keyboard import main_menu_keyboard,\
    show_bills_keyboard

from retail.models import Customer


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


MAIN_MENU, REMOVE_FAVORITE_BILLS = 0, 7


def get_or_create_user(update: Update) -> Customer:
    user, _ = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id
    )
    return user


def handle_my_accounts(update: Update, context: CallbackContext, user: Customer) -> int:
    user_bills = [str(favorite.bill.value) for favorite in user.favorites.all()]
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
    context.user_data['prev_step'] = 'choose'
    return REMOVE_FAVORITE_BILLS


def update_main_menu(update: Update, context: CallbackContext, user: Customer) -> int:
    if user.favorites.count() > 0:
        context.user_data['bills_count'] = user.favorites.count()
        bills = True
    else:
        bills = False
    update.message.reply_text(
        "Выберите раздел",
        reply_markup=main_menu_keyboard(bills)
    )
    return MAIN_MENU


def handle_main_menu(update: Update, context: CallbackContext) -> int:
    logger.info("main_menu.py") 
    text = update.message.text
    user = get_or_create_user(update)

    if text == "Мои лицевые счета" and user.favorites.count() > 0:
        return handle_my_accounts(update, context, user)
    elif text == "Передать показания счётчиков":
        context.user_data['prev_step'] = 'main'
        return submit_readings(update, context)
    elif text == "Приборы учёта":
        return get_meter_info(update, context)
    elif text == "Контакты и режим работы":
        return get_contact_info(update, context)
    elif text == "В главное меню":
        return update_main_menu(update, context, user)
    else:
        return update_main_menu(update, context, user)  


def fallback(update: Update, context: CallbackContext) -> int:
    logger.warning("fallback")
    update.message.reply_text(
        "Не понял команду. Давайте начнем сначала.",
        reply_markup=main_menu_keyboard()
    )
    return handle_start(update, context)
