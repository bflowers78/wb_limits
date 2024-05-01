from config.config import TOKEN_BOT, MY_ID
from params import warehouses, cargos, interested_time, limit_values
from db.sql import SQL
from main import initial_check
from keyboards import *
import telebot

bot = telebot.TeleBot(TOKEN_BOT)


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
            При выборе платной приемки бот будет искать указанный коэффициент или ниже\n
            Например:\n Выбрано "До x2" - бот ищет: бесплатную, x1 и x2 приемки'''
        },
    ]

    def __init__(self, user_id):
        self.id = user_id
        self.__wh_iter = 0
        self.__step = 0
        self.data = {
            'user_id': user_id,
            'warehouse': None,
            'cargo': None,
            'time': None,
            'limit_values': None,
        }
        User_api.users[user_id] = self

    @property
    def step(self):
        return self.__step

    @step.setter
    def step(self, index):
        if index > 3:
            self.__step = 0
        else:
            self.__step = index

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
        markup = wh_keyboard_generation(self.wh_iter) if self.step == 0 else self.STEPS[self.step]['buttons']
        bot.send_message(self.id, self.STEPS[self.step]['message'], reply_markup=markup)

    def check_and_write(self, call):
        """Проверка полученных данных и запись в SQL таблицу"""
        if all(value for value in self.data.values()):
            SQL.add_request(tuple(self.data.values()))  # Запись в БД
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(self.id, 'Данные успешно записаны. Ведется поиск...', reply_markup=main_menu())
            User_api.users.pop(self.id)
            initial_check(self.data)
            return True

    def next_step(self, call):
        """Проверка комплектности данных проводник между запросами"""
        if self.check_and_write(call): return
        self.step += 1
        bot.delete_message(call.message.chat.id, call.message.message_id)
        self.send_request()


@bot.callback_query_handler(func=lambda call: call.data == 'new_request')
def create_request(call):
    """Создание нового запроса"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if SQL.check_limit(call.message.chat.id):  # Проверка колличества записей
        user_obj = User_api(call.message.chat.id)
        user_obj.send_request()
    else:
        bot.send_message(call.message.chat.id,
                         'Добавление записи отклонено.\nВозможно иметь только 11 активных записей.',
                         reply_markup=main_menu())


@bot.callback_query_handler(func=lambda call: call.data == 'my_requests')
def get_requests(call):
    """Получение всех запросов пользователя"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_requests = SQL.get_requests(call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Ваши запросы:', reply_markup=show_requests(user_requests))


@bot.callback_query_handler(func=lambda call: call.data.split('.')[0] == 'del')
def del_requests(call):
    """Удаление запросов"""
    request_id = call.data.split('.')[1]
    SQL.del_request(request_id)
    get_requests(call)


@bot.callback_query_handler(func=lambda call: call.data == 'main')
def back(call):
    """Возврат к главному меню"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'Главное меню', reply_markup=main_menu())


@bot.callback_query_handler(func=lambda call: call.data == 'next')
def next_wh(call):
    """Переход к следующемму набору складов"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_obj = User_api.users[call.message.chat.id]
    user_obj.wh_iter += 1
    user_obj.send_request()


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_wh(call):
    """Возврат к предидущему набору складов"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_obj = User_api.users[call.message.chat.id]
    user_obj.wh_iter -= 1
    user_obj.send_request()


@bot.callback_query_handler(func=lambda call: call.data)
def calldata_handler(call):
    """Прием входящих каллбэков и сохранение данных под нужным ключом"""
    try:
        type_data = data_is(call.data)

        if type_data:
            user_obj = User_api.users[call.message.chat.id]
            user_obj.data[type_data] = call.data
            user_obj.next_step(call)
    except KeyError:
        bot.send_message(call.message.chat.id, 'Главное меню', reply_markup=main_menu())


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


@bot.message_handler(commands=['start'])
def start(message):
    """Начало работы с ботом"""
    bot.send_message(message.chat.id, '''Этот бот служит для поиска необходимых слотов для отгрузки на склады Wildberries.
    Для того чтобы начать поиск создайте новый запрос.''', reply_markup=main_menu())


if __name__ == '__main__':
    bot.infinity_polling()
