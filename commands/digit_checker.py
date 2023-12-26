

def digit_checker(update, context, step, user):
    text = update.message.text
    if text in ["Как узнать лицевой счёт", "В главное меню", 'Ввести другой', 'Передать показания счётчиков']:
        return step
    elif text.isdigit() and user.favorites.filter(bill__value=int(text)).exists():
        return step
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не понял команду. Давайте начнем сначала."
        )
        return step
