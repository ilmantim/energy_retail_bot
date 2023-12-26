from keyboard import go_to_main_menu_keyboard

MAIN_MENU, SUBMIT_READINGS, INPUT_READINGS, YES_OR_NO_ADDRESS, METER_INFO, \
    CONTACT_INFO, CREATE_FAVORITE_BILL, REMOVE_FAVORITE_BILLS = range(8)


def send_info(update, context, bill_here, submit=False):
    registration_date_str = (
        bill_here.registration_date.date().strftime("%Y-%m-%d")
        if bill_here.registration_date else "Дата не указана"
    )
    readings_str = str(
        bill_here.readings) + ' квт*ч' if bill_here.readings is not None else "Показания не указаны"
    number_and_type_pu_str = bill_here.number_and_type_pu if bill_here.number_and_type_pu else "Номер и тип ПУ не указаны"
    if submit:
        update.message.reply_text(
            f'Лицевой счет: {bill_here.value}\n'
            f'Номер и тип ПУ: {number_and_type_pu_str}\n'
            f'Показания: {readings_str}\n'
            f'Дата приёма: {registration_date_str}\n'
            'Введите новые показания:',
            reply_markup=go_to_main_menu_keyboard()
        )
        return INPUT_READINGS
    else:
        update.message.reply_text(
            f'Лицевой счет: {bill_here.value}\n'
            f'Номер и тип ПУ: {number_and_type_pu_str}\n'
            f'Показания: {readings_str}\n'
            f'Дата приёма: {registration_date_str}\n',
            reply_markup=go_to_main_menu_keyboard()
        )
        return MAIN_MENU