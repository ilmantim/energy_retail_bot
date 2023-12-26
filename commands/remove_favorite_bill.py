import logging

from telegram import Update
from telegram.ext import CallbackContext
from retail.models import Customer

from keyboard import main_menu_keyboard,\
    show_bills_keyboard, delete_bills_keyboard

from commands.start import handle_start


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
    )
logger = logging.getLogger(__name__)


MAIN_MENU, REMOVE_FAVORITE_BILLS = 0, 7


def remove_favorite_bill(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user, is_found = Customer.objects.get_or_create(
        chat_id=update.effective_chat.id
    )

    if (
        text.isdigit() and user.favorites.filter(bill__value=int(text)).exists()
    ) and not context.user_data['prev_step'] == 'choose':
        user.favorites.get(bill__value=int(text)).delete()
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
        context.user_data['prev_step'] = 'choose'
        update.message.reply_text(
            "Выберите нужный пункт снизу.",
            reply_markup=show_bills_keyboard()
        )
        return REMOVE_FAVORITE_BILLS
    
    elif text == 'Главное меню':
        return handle_start(update, context)
    
    elif text == "Удалить лицевой счёт":
        context.user_data['prev_step'] = 'delete'
        user, is_found = Customer.objects.get_or_create(
            chat_id=update.effective_chat.id
        )
        user_bills = [
            [str(favorite.bill.value)] for favorite in user.favorites.all()
        ]
        update.message.reply_text(
            "Выберите лицевой счёт, который Вы хотите удалить.",
            reply_markup=delete_bills_keyboard(user_bills)
        )
        return REMOVE_FAVORITE_BILLS
    else:
        update.message.reply_text(
            "Не понял команду. Давайте начнем сначала.",
            reply_markup=show_bills_keyboard()
        )
        return REMOVE_FAVORITE_BILLS
