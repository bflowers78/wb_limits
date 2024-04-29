from config.config import TOKEN_BOT, MY_ID
from params import warehouses, warehouses_split, cargos, interested_time, limit_values
from telebot import types
import telebot

bot = telebot.TeleBot(TOKEN_BOT)


def keyboard_generation(data_list):
    """Генерация клавиатуры на основе списка с данными"""
    markup = types.InlineKeyboardMarkup()
    for data in data_list:
        markup.add(types.InlineKeyboardButton(data, callback_data=data))
    return markup


class User_api:
    users = {}
    STEPS = [
        {
            'message': 'Выберете интересущий вас склад:',
        },
        {
            'buttons': keyboard_generation(cargos),
            'message': 'Выберете тип груза'
        },
        {
            'buttons': keyboard_generation(interested_time),
            'message': 'Выберете время для поиска'
        },
        {
            'buttons': keyboard_generation(limit_values),
            'message': '''Выберите тип приёмки, на который будем искать слот
            При выборе платной приемки бот будет искать указанный коэффициент или ниже
            Например: Выбрано "До x2" - бот ищет: бесплатную, x1 и x2 приемки'''
        },
    ]

    def __init__(self, user_id):
        self.id = user_id
        self.__wh_iter = 0
        self.step = 0
        self.data = {
            'warehouse': None,
            'cargo': None,
            'time': None,
            'limit_values': None,
        }
        User_api.users[user_id] = self
        self.show_warehouses()

    @property
    def wh_iter(self):
        return self.__wh_iter

    @wh_iter.setter
    def wh_iter(self, index):
        if index > 9:
            self.__wh_iter = 0
        else:
            self.__wh_iter = index

    def send_request(self):
        markup = self.wh_keyboard_generation() if self.step == 0 else self.STEPS[self.step]
        bot.send_message(self.id, self.STEPS[self.step]['message'], reply_markup=markup)

    def wh_keyboard_generation(self):
        """Возвращает клавиатуру с набором складов в зависимости от текущего индекса пользователя"""
        markup = types.InlineKeyboardMarkup()
        for warehouse in warehouses_split[self.wh_iter]:
            markup.add(types.InlineKeyboardButton(warehouse, callback_data=warehouse))
        if self.wh_iter == 0:
            markup.add(types.InlineKeyboardButton('Далее', callback_data='next'))
        else:
            markup.row(types.InlineKeyboardButton('Назад', callback_data='back'),
                       types.InlineKeyboardButton('Далее', callback_data='next'))
        return markup

    def check_and_write(self):
        """Проверка полученных данных и запись в SQL таблицу"""
        if all(value for value in self.data.values()):
            pass

    @staticmethod
    def keyboard_generation(data_list):
        """Генерация клавиатуры на основе списка с данными"""
        markup = types.InlineKeyboardMarkup()
        for data in data_list:
            markup.add(types.InlineKeyboardButton(data, callback_data=data))
        return markup


@bot.callback_query_handler(func=lambda call: call.data == 'next')
def next_wh(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_obj = User_api.users[call.message.chat.id]
    user_obj.wh_iter += 1
    user_obj.show_warehouses()


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_wh(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_obj = User_api.users[call.message.chat.id]
    user_obj.wh_iter -= 1
    user_obj.show_warehouses()


@bot.callback_query_handler(func=lambda call: call.data)
def calldata_handler(call):
    """Прием входящих каллбэков и сохранение данных под нужным ключом"""
    user_obj = User_api.users[call.message.chat.id]
    type_data = data_is(call.data)

    if type_data: user_obj.wh_iter[type_data] = call.data
    if user_obj.check_and_write(): return
    user_obj.next_step()


def data_is(call_data):
    """Определяет и возвращает к какой категории относится каллбэк"""
    if call_data in warehouses:
        return 'warehouse'
    elif call_data in cargos:
        return 'cargo'
    elif call_data in interested_time:
        return 'time'
    elif call_data in limit_values:
        return 'limit_values'
    else:
        bot.send_message(MY_ID, f'Непонятно как но call.data is {call_data}')


@bot.message_handler(commands=['start'])
def start(message):
    """Начало работы с ботом"""
    User_api(message.chat.id)


if __name__ == '__main__':
    bot.infinity_polling()
