from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from config.config import TOKEN_BOT
from params import params
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


class Seance:
    OPTIONS_CHROME = webdriver.ChromeOptions()
    #options_chrome.add_argument('--headless')
    #options_chrome.add_argument('--proxy-server=192.109.100.157:8000')
    MY_ID = 382052667

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
        if len(nums) != 6: pass  # ошибка
        for cell, num in zip(cells, nums):
            cell.send_keys(num)

        time.sleep(2)
        if self.driver.current_url != params['url']:
            self.get_sms_code()

        bot.send_message(self.MY_ID, 'Успешный вход')
        self.parsing()

    def create_dict_limits(self):
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
        print(data)
        return data

    def parsing(self):
        while True:
            print('Зашли в цикл')
            seance.driver.get('https://seller.wildberries.ru/supplies-management/warehouses-limits')
            print('браузер обновлен')
            time.sleep(2)
            changes = check_changes(seance.create_dict_limits())
            if changes: rotor_changes(changes)
            print('seleep')
            time.sleep(60)
            print('закончили sleep')


def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_data():
    with open('data.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def check_changes(data_new):
    '''Функция проверяет два словаря, находит изменения в новом
        и возвращает список с изменениями в формате:
         [key, key, key, value]'''
    changes = []
    data_old = get_data()
    if data_new == data_old: return None

    for date in data_new.keys():
        for warehouse in data_new[date].keys():
            for cargo in data_new[date][warehouse].keys():
                print(data_old[date][warehouse].keys(), data_new[date][warehouse].keys())
                if date in data_old and data_old[date][warehouse][cargo] != data_new[date][warehouse][cargo]:
                    changes.append([date, warehouse, cargo, data_new[date][warehouse][cargo]])
    save_data(data_new)
    return changes


def rotor_changes(changes):
    print('ротор чанджес')
    for date, wh, cargo, value in changes:
        if wh in wh_interest and cargo == 'Короба':
            bot.send_message(Seance.MY_ID, f'Произошли изменения: {date} / {wh} / {value}')


if __name__ == '__main__':
    seance = Seance()
    bot.infinity_polling()
    print('сеанс создан')
    while True:
        print('Зашли в цикл')
        seance.driver.get(params['url'])
        print('браузер обновлен')
        changes = check_changes(seance.create_dict_limits())
        if changes: rotor_changes(changes)
        print('seleep')
        time.sleep(60)
        print('закончили sleep')
