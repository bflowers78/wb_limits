from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from config.config import TOKEN_LOGS, MY_ID, TOKEN_BOT
from params import params, cargos
from db.sql import SQL
from datetime import datetime, timedelta
import telebot
import time
import json
bot_log = telebot.TeleBot(TOKEN_LOGS)
bot = telebot.TeleBot(TOKEN_BOT)
wh_interest = ['Коледино', 'Электросталь', 'Тула', 'СЦ Внуково']


class Seance:
    OPTIONS_CHROME = webdriver.ChromeOptions()
    #options_chrome.add_argument('--headless')
    #options_chrome.add_argument('--proxy-server=192.109.100.157:8000')

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
        """Отправка администратору картинки с капчей, для ее разгадывания"""
        captcha = self.get_element(params['load_captcha'])
        captcha.screenshot('captcha_screenshot.png')
        captcha_answer = bot_log.send_photo(MY_ID, open('captcha_screenshot.png', "rb"))
        bot_log.register_next_step_handler(captcha_answer, self.send_captcha_answer)

    def send_captcha_answer(self, captcha_answer):
        """Вставляем полученную от администратора разшифрованную капчу"""
        self.get_element(params['input_captcha']).send_keys(captcha_answer.text)
        self.get_element(params['button_captcha']).click()

        # Проверка валидности
        try:
            time.sleep(2)
            self.get_element(params['button_captcha'])
            self.send_captcha_screenshot()
        except:
            self.get_sms_code()

    def get_sms_code(self):
        """Получение от администратора СМС кода"""
        sms_code = bot_log.send_message(MY_ID, 'Captcha введена верно, отправте код из СМС')
        bot_log.register_next_step_handler(sms_code, self.send_sms_code)

    def send_sms_code(self, sms_code):
        """Вставка полученного СМС кода"""
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
            bot_log.send_message(MY_ID, 'Успешный вход')
            self.parsing()

    def create_dict_limits(self):
        """Парсинг страницы с лимитами и формирование словаря с данными"""
        warehouses = [x.text for x in self.driver.find_elements(By.XPATH, params['warehouses'])]
        cells = [[a.find_elements(By.XPATH, params['cells']) for a in b.find_elements(By.CLASS_NAME, 'Limits-table__table-row__F01IcFLtBl')] for b in self.driver.find_elements(By.XPATH, "//div[@class='Limits-table__table-body__kR9Q+dx9Dm']")]
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
        bot_log.send_message(MY_ID, 'Бот вернул пустой словарь')
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
                            bot_log.send_message(MY_ID, f'Ключ {e.args[0]} отсутствует в старом словаре')
                            time.sleep(1)
        save_data(data_new)
        return changes


def get_week_dates() -> list:
    return get_data().keys()


def rotor_changes(changes: list):
    """Итерация по изменениям отправка интересующих их данных пользователям"""
    user_dates = SQL.get_requests()
    print('user_dates',user_dates)
    print('changes', changes)
    for date, wh, cargo, value in changes:
        # Итератор по пользователям
        for user_id, u_wh, u_cargo, u_date, u_value in user_dates:
            if wh == u_wh and cargo == u_cargo:
                # Сверка дат и сверка значений, нужно добавить новые функции
                if date_comparsion(date, u_date) and value_comparsion(value, u_value):
                    bot.send_message(user_id, f'''Найден новый слот:\n Дата: {date}\n Склад: {wh}\n Груз: {cargo}\n Значение: {value}''')
                    time.sleep(2)


def date_comparsion(date: str, u_date: str) -> bool:
    """Сравнение значений дат"""
    print(date, u_date, transform_date(datetime.today().strftime('%d.%m')))
    if u_date == 'сегодня' and date == transform_date(datetime.today().strftime('%d.%m')):
        print("True")
        return True
    elif u_date == 'завтра' and date == transform_date((datetime.today() + timedelta(days=1)).strftime('%d.%m')):
        print('Завтра')
        return True
    elif u_date == 'неделя' and date in get_week_dates():
        return True
    elif u_date == 'искать пока не найдется':
        return True
    return False


def value_comparsion(value: str, u_value: str) -> bool:
    print(value, u_value)
    if value == 'Временно недоступно':
        return False
    elif value == 'Бесплатно':
        return True
    elif int(value[-1]) <= int(u_value[-1]):
        return True
    return False


def validate_dates(u_date: str) -> list:
    week_dates = get_week_dates()
    valid_dates = []
    for date in week_dates:
        if date_comparsion(date, u_date):
            valid_dates.append(date)
    return valid_dates


def initial_check(user_data: dict):
    """Начальная проверка введенных данных"""
    date_validate = validate_dates(user_data['time'])
    print(date_validate)
    warehouse = user_data['warehouse']
    cargo = user_data['cargo']
    u_value = user_data['limit_values']
    print(warehouse, cargo, u_value)
    data = get_data()
    for date in date_validate:
        value = data[date][warehouse][cargo]
        print('value', value)
        if value_comparsion(value, u_value):
            bot.send_message(user_data['user_id'], f'''Найден новый слот:\n Дата: {date}\n Склад: {warehouse}\n Груз: {cargo}\n Значение: {value}''')
            time.sleep(1)
    # Нужно добавить логику с удалением только что добавленной записи


def transform_date(date):

    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    day, month = date.split('.')
    return f'{day} {months[int(month) - 1]}'


if __name__ == '__main__':
    seance = Seance()
    bot_log.infinity_polling()

