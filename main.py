from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from telebot import types
from selenium import webdriver
from config.config import TOKEN_BOT
from params import params, warehouses
import telebot
import time
import json
####################################

'''
1 Выбираем склад
2 Тип поставки (коробки, палеты, суперсейф)
3 Тип приемки (бесплатная, х1)
4 Выбор даты (сегодня, завтра, неделя, ввести дату, искать пока не найдется)
Можно сделать кучу
Мои запросы:'''
bot = telebot.TeleBot(TOKEN_BOT)
wh_interest = ['Коледино', 'Электросталь', 'Тула', 'СЦ Внуково']


# class Handler:
#     @bot.message_handler(commands=['start'])
#     def __init__(self, message):
#         """Начало работы с ботом"""
#         self.id = message.chat.id
#         self.wh_iter = 0
#         self.show_warehouses()
#
#     def show_warehouses(self):
#         wh_buttons = self.button_generation()
#         bot.send_message(self.id, 'Выберете интересущий вас склад:', reply_markup=wh_buttons)
#
#     def button_generation(self):
#         """Возвращает клавиатуру с набором складов в зависимости от индекса"""
#         markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
#         for warehouse in warehouses[self.id]:
#             markup.add(telebot.types.KeyboardButton(warehouse))
#         if self.id == 0:
#             markup.add(types.InlineKeyboardButton('Далее', callback_data='next'))
#         else:
#             markup.row(types.InlineKeyboardButton('Назад', callback_data='back'),
#                        types.InlineKeyboardButton('Далее', callback_data='next'))
#         return markup
#
#     @bot.callback_query_handler(func=lambda call: call.data == 'next')
#     def next_wh(self, call):
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         self.id += 1
#         self.show_warehouses()
#
#     @bot.callback_query_handler(func=lambda call: call.data == 'back')
#     def back_wh(self, call):
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         self.id -= 1
#         self.show_warehouses()

class Seance:
    OPTIONS_CHROME = webdriver.ChromeOptions()
    #options_chrome.add_argument('--headless')
    #options_chrome.add_argument('--proxy-server=192.109.100.157:8000')
    MY_ID = 470671108 #382052667

    def __init__(self):
        self.driver = webdriver.Chrome(options=self.OPTIONS_CHROME)
        self.driver.get('https://seller.wildberries.ru/')
        time.sleep(1)
        self.get_element(params['start_authorization']).click()
        self.driver.find_element(By.TAG_NAME, "input").send_keys("9650626812")
        self.driver.find_element(By.CLASS_NAME, 'FormPhoneInputBorderless__image--qsIVS').click()
        self.send_captcha_screenshot()

    def get_element(self, XPATH, time=3, alone=True):
        if alone:
            return WebDriverWait(self.driver, time).until(EC.presence_of_element_located((By.XPATH, XPATH)))
        else:
            return WebDriverWait(self.driver, time).until(EC.presence_of_all_elements_located((By.XPATH, XPATH)))

    def send_captcha_screenshot(self):
        captcha = self.get_element(params['load_captcha'])
        captcha.screenshot('captcha_screenshot.png')
        captcha_answer = bot.send_photo(self.MY_ID, open('captcha_screenshot.png', "rb"))
        bot.register_next_step_handler(captcha_answer, self.send_captcha_answer)

    def send_captcha_answer(self, captcha_answer):
        self.get_element(params['input_captcha']).send_keys(captcha_answer.text)
        self.get_element(params['button_captcha']).click()
        try:
            time.sleep(2)
            self.get_element(params['button_captcha'])
            self.send_captcha_screenshot()
        except:
            self.get_sms_code()

    def get_sms_code(self):
        sms_code = bot.send_message(self.MY_ID, 'Captcha введена верно, отправте код из СМС')
        bot.register_next_step_handler(sms_code, self.send_sms_code)

    def send_sms_code(self, sms_code):
        nums = sms_code.text
        cells = self.get_element(params['input_sms_code'], alone=False)
        if len(nums) != 6: # Нужно будет потестировать данную тему
            print(len(nums))
            # sms_code = bot.send_message(self.MY_ID, 'Ожидается 6-ти значный код. Введи заного или заново')
            # bot.register_next_step_handler(sms_code, self.send_sms_code)
        for cell, num in zip(cells, nums):
            cell.send_keys(num)
        time.sleep(2)

        if self.driver.current_url != params['url']:  # работает не корректно
            self.get_sms_code()
        else:
            bot.send_message(self.MY_ID, 'Успешный вход')
            self.parsing()

    def create_dict_limits(self):
        """Парсинг страницы с лимитами и формирование словаря с данными"""
        cargos = ['Короба', 'Монопаллеты', 'Суперсейф', 'QR-поставка с коробами']
        warehouses = [x.text for x in self.driver.find_elements(By.XPATH, params['warehouses'])]
        cells = [[a.find_elements(By.TAG_NAME, 'span') for a in b.find_elements(By.CLASS_NAME, 'Limits-table__table-row__F01IcFLtBl')] for b in self.driver.find_elements(By.XPATH, "//div[@class='Limits-table__table-body__kR9Q+dx9Dm']")]
        dates = [x.text for x in self.driver.find_elements(By.XPATH, params['dates'])][2:]

        # Формирование словаря
        data = {}
        for i, date in enumerate(dates):
            data[date] = {}
            for wh, wh_cells in zip(warehouses, cells):
                data[date][wh] = {}
                for cargo, cell in zip(cargos, wh_cells):
                    data[date][wh][cargo] = cell[i].text
        return data

    def parsing(self):
        try:
            while True:
                seance.driver.get('https://seller.wildberries.ru/supplies-management/warehouses-limits')
                time.sleep(5)
                changes = check_changes(seance.create_dict_limits())
                if changes: rotor_changes(changes)
                time.sleep(60)
        except:
            pass


def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_data():
    with open('data.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def check_changes(data_new):
    """Функция проверяет два словаря, находит изменения в новом
        и возвращает список с изменениями в формате:
         [key, key, key, value]"""

    changes = []
    data_old = get_data()
    if not data_new:
        bot.send_message(Seance.MY_ID, 'Бот вернул пустой словарь')
        return
    if data_new == data_old:
        print('Без изменений')
        return

    for date in data_new.keys():
        if date in data_old:
            for warehouse in data_new[date].keys():
                    for cargo in data_new[date][warehouse].keys():
                        try:
                            if data_old[date][warehouse][cargo] != data_new[date][warehouse][cargo]:
                                changes.append([date, warehouse, cargo, data_new[date][warehouse][cargo]])
                        except KeyError as e:
                            bot.send_message(Seance.MY_ID, f'Ключ {e.args[0]} отсутствует в старом словаре')
                            time.sleep(1)
        save_data(data_new)
        return changes


def rotor_changes(changes):
    """Итерация по изменениям отправка интересующих их данных пользователям"""
    for date, wh, cargo, value in changes:
        if wh in wh_interest and cargo == 'Короба' and value == 'Бесплатно':
            bot.send_message(Seance.MY_ID, f'Произошли изменения: {date} / {wh} / {value}')
            time.sleep(2)


if __name__ == '__main__':
    seance = Seance()
    bot.infinity_polling(non_stop=True)

