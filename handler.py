from config.config import TOKEN_BOT
from params import warehouses
from telebot import types
import telebot

bot = telebot.TeleBot(TOKEN_BOT)


class Handler:
    @bot.message_handler(commands=['start'])
    def __init__(self, message):
        """Начало работы с ботом"""
        self.id = message.chat.id
        self.wh_iter = 0
        self.show_warehouses()

    def show_warehouses(self):
        wh_buttons = self.button_generation()
        bot.send_message(self.id, 'Выберете интересущий вас склад:', reply_markup=wh_buttons)

    def button_generation(self):
        """Возвращает клавиатуру с набором складов в зависимости от индекса"""
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
        for warehouse in warehouses[self.id]:
            markup.add(telebot.types.KeyboardButton(warehouse))
        if self.id == 0:
            markup.add(types.InlineKeyboardButton('Далее', callback_data='next'))
        else:
            markup.row(types.InlineKeyboardButton('Назад', callback_data='back'),
                       types.InlineKeyboardButton('Далее', callback_data='next'))
        return markup

    @bot.callback_query_handler(func=lambda call: call.data == 'next')
    def next_wh(self, call):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        self.id += 1
        self.show_warehouses()

    @bot.callback_query_handler(func=lambda call: call.data == 'back')
    def back_wh(self, call):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        self.id -= 1
        self.show_warehouses()


if __name__ == '__main__':
    bot.infinity_polling(non_stop=True)
