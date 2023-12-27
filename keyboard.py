from telegram import ReplyKeyboardMarkup


def yes_or_no_keyboard():
    return ReplyKeyboardMarkup(
        [["Да", "Нет"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def yes_and_no_keyboard():
    return ReplyKeyboardMarkup(
        [["Да"], ["Нет"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def go_to_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [["В главное меню"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def main_menu_keyboard(bills=False):
    if not bills:
        info = [
            ["Передать показания счётчиков"],
            ["Приборы учёта"],
            ["Контакты и режим работы"]
        ]
    else:
        info = [
            ["Передать показания счётчиков"],
            ["Приборы учёта"],
            ["Мои лицевые счета"],
            ["Контакты и режим работы"]
        ]
    return ReplyKeyboardMarkup(
        info,
        resize_keyboard=True,
        one_time_keyboard=True
    )


# def main_menu_with_bills_keyboard():
#     return ReplyKeyboardMarkup([
#         ["Передать показания счётчиков"],
#         ["Приборы учёта"],
#         ["Мои лицевые счета"],
#         ["Контакты и режим работы"]
#     ],
#         resize_keyboard=True,
#         one_time_keyboard=True
#     )


def submit_readnigs_and_get_meter_keyboard(info=None):
    if info is None:
        info = [
            ["Как узнать лицевой счёт"],
            ["В главное меню"]
        ]
    else:
        info.append(['Ввести другой'])
        info.append(["Как узнать лицевой счёт", "В главное меню"])
    return ReplyKeyboardMarkup(
        info,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def submit_readnigs_and_get_meter_with_bills_keyboard():
    return ReplyKeyboardMarkup([
        ["Здесь должны быть избранные счета"],
        # сюда добавляется избранный счёт
        ["Ввести другой"],
        ["Где найти лицевой счёт", "Главное меню"]
    ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def show_bills_keyboard():
    return ReplyKeyboardMarkup([
        ["Удалить лицевой счёт"],
        ["Главное меню"]
    ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def delete_bills_keyboard(info):
    info.append(["Назад", "Главное меню"])
    return ReplyKeyboardMarkup(
        info,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def choose_MRO_keyboard():
    return ReplyKeyboardMarkup([
        ["Чебоксарское МРО"],
        ["Алатырское МРО"],
        ["Батыревское МРО"],
        ["Канашское МРО"],
        ["Новочебоксарское МРО"],
        ["Цивильское МРО"],
        ["Шумерлинское МРО"],
        ["Ядринское МРО"],
        ["Управление"],
        ["Главное меню"]
    ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def choose_address_keyboard(addresses):
    return ReplyKeyboardMarkup(
        [
            addresses,
            ["Главное меню"]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )