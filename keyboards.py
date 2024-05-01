from telebot import types
from params import warehouses_split


def wh_keyboard_generation(wh_iter: int) -> types:
    """Возвращает клавиатуру с набором складов в зависимости от текущего индекса пользователя"""
    markup = types.InlineKeyboardMarkup()
    for warehouse in warehouses_split[wh_iter]:
        markup.add(types.InlineKeyboardButton(warehouse, callback_data=warehouse))
    if wh_iter == 0:
        markup.add(types.InlineKeyboardButton('Далее', callback_data='next'))
    else:
        markup.row(types.InlineKeyboardButton('Назад', callback_data='back'),
                   types.InlineKeyboardButton('Далее', callback_data='next'))
    return markup


def keyboard_generation(data_list: list) -> types:
    """Генерация клавиатуры на основе списка с данными"""
    markup = types.InlineKeyboardMarkup()
    for data in data_list:
        markup.add(types.InlineKeyboardButton(data, callback_data=data))
    return markup


def keyboard_start() -> types:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Новый запрос', callback_data='new_request'))
    return markup


def main_menu() -> types:
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Новый запрос', callback_data='new_request'))
    markup.add(types.InlineKeyboardButton('Мои запросы', callback_data='my_requests'))
    return markup


def show_requests(requests: list) -> types:
    """Возвращает все запросы пользователя в виде инлайн кнопок"""
    markup = types.InlineKeyboardMarkup(row_width=5)
    for row in requests:
        requests_id = row[0]
        markup.add(types.InlineKeyboardButton(row[2], callback_data='None'),
                   types.InlineKeyboardButton(row[3], callback_data='None'),
                   types.InlineKeyboardButton(row[4], callback_data='None'),
                   types.InlineKeyboardButton(row[5], callback_data='None'),
                   types.InlineKeyboardButton('❌', callback_data=f'del.{requests_id}'))
    markup.add(types.InlineKeyboardButton('Назад', callback_data='main'))
    return markup
