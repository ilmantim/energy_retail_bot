import logging

from telegram import Update
from telegram.ext import CallbackContext

from retail.models import Mro
from keyboard import main_menu_keyboard, choose_MRO_keyboard, choose_address_keyboard
from commands.start import handle_start


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)


CONTACT_INFO = 5


def get_contact_info(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    prev_department = context.user_data.get('prev_department', None)

    if text.isdigit() and prev_department:
        try:
            department_here = Mro.objects.get(name=prev_department)
            address_here = department_here.addresses.get(num=int(text))
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=address_here.name
            )
            return handle_start(update, context)
        except (
            Mro.DoesNotExist, department_here.addresses.model.DoesNotExist
        ):
            logger.error(
                f"Address or department not found for {prev_department} with number {text}"
            )
            update.message.reply_text(
                "Не найдено. Пожалуйста, выберите снова.", 
                reply_markup=choose_MRO_keyboard()
            )
            return CONTACT_INFO

    elif text == "Главное меню":
        return handle_start(update, context)

    elif Mro.objects.filter(name=text).exists():
        department = Mro.objects.get(name=text)
        if department.addresses.count() > 0:
            addresses = [
                str(i + 1) for i in range(department.addresses.count())
            ]
            context.user_data['prev_department'] = department.name
            update.message.reply_text(
                department.general, 
                reply_markup=choose_address_keyboard(addresses)
            )
            update.message.reply_text(
                "Выберите номер удобного для Вас МРО в меню снизу"
            )
            return CONTACT_INFO
        else:
            update.message.reply_text(
                department.general, reply_markup=main_menu_keyboard()
            )
            return handle_start(update, context)

    else:
        update.message.reply_text(
            "Выберите МРО", reply_markup=choose_MRO_keyboard()
        )
        return CONTACT_INFO