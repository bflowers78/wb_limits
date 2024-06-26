params = {
    'url'                   : 'https://seller.wildberries.ru/?skipLanding',
    'start_authorization'   : "//span[@class='Text--sQ5H2 Text--size-m--NIoHX Text--color-White--csIrI']",
    'load_captcha'          : "//img[@class='CaptchaFormContentView__captcha--8FDAG']",
    'input_captcha'         : "//input[@class='SimpleInput--9m9Pp SimpleInput--color-RichGreyNew--4z4Nb SimpleInput--centered--ZmsXW']",
    'button_captcha'        : "//span[@class='Text--sQ5H2 Text--size-xl--N+UTw Text--color-SuperDuperLightGrey--ENlxM']",
    'input_sms_code'        : "//input[@class='InputCell--7FpiE']",
    'warehouses'            : "//div[@class='Limits-table__warehouse-item__9EKMBScgVB']",
    'wh_cargos'             : "//div[@class='Limits-table__table-body__kR9Q+dx9Dm']",
    'dates'                 : "//span[@class='Text__jKJsQramuu Text--h5-bold__FFXh7Nn6bh Text--black__hIzfx5PELf']",
    'cells'                 : "//div[@class='Coefficient-table-cell__EqV0w0Bye8']",#"//div[@class='Table-cell-item__ZCLGoPuD+I']",
}
cargos = ['Короба', 'Монопаллеты', 'Суперсейф', 'QR-поставка с коробами']
interested_time = ['сегодня', 'завтра', 'неделя', 'искать пока не найдется']  # Ввести дату добавлю позже
limit_values = ['Бесплатно', '< x1', '< x2', '< x3', '< x4']
warehouses = [
    "Алматы Атакент", "Астана", "Белые Столбы", "Внуково СГТ", "Волгоград", "Вёшки", "Екатеринбург - Испытателей 14г", "Екатеринбург - Перспективный 12/2", "Казань", "Коледино",
    "Котовск", "Краснодар (Тихорецкая)", "Минск", "Невинномысск", "Новосемейкино", "Новосибирск", "Обухово", "Обухово 2", "Обухово СГТ", "Подольск",
    "Подольск 3", "Подольск 4", "Пушкино", "Радумля СГТ", "Рязань (Тюшевское)", "СЦ Абакан", "СЦ Абакан 2", "СЦ Артем", "СЦ Архангельск (ул Ленина)", "СЦ Астрахань",
    "СЦ Астрахань (Солянка)", "СЦ Байсерке", "СЦ Барнаул", "СЦ Белая Дача", "СЦ Белогорск", "СЦ Бишкек", "СЦ Владикавказ", "СЦ Владимир", "СЦ Внуково", "СЦ Волгоград 2",
    "СЦ Вологда", "СЦ Вологда 2", "СЦ Воронеж", "СЦ Иваново", "СЦ Ижевск", "СЦ Иркутск", "СЦ Калуга", "СЦ Кемерово", "СЦ Киров", "СЦ Киров (old)",
    "СЦ Крыловская", "СЦ Кузнецк", "СЦ Курск", "СЦ Липецк", "СЦ Махачкала", "СЦ Мурманск", "СЦ Набережные Челны", "СЦ Нижний Новгород", "СЦ Нижний Тагил", "СЦ Новокузнецк",
    "СЦ Новосибирск Пасечная", "СЦ Омск", "СЦ Оренбург", "СЦ Ош", "СЦ Пермь 2", "СЦ Псков", "СЦ Пятигорск", "СЦ Пятигорск (Этока)", "СЦ Радумля", "СЦ Ростов-на-Дону",
    "СЦ Самара", "СЦ Саратов", "СЦ Семей", "СЦ Серов", "СЦ Симферополь", "СЦ Смоленск 3", "СЦ Сургут", "СЦ Сыктывкар", "СЦ Тамбов", "СЦ Тверь",
    "СЦ Томск", "СЦ Тюмень", "СЦ Ульяновск", "СЦ Уральск", "СЦ Уфа", "СЦ Хабаровск", "СЦ Челябинск 2", "СЦ Чита 2", "СЦ Чёрная Грязь", "СЦ Шушары",
    "СЦ Шымкент", "СЦ Ярославль", "Санкт-Петербург (Уткина Заводь)", "Сц Брянск 2", "Тула", "Хабаровск", "Чехов 1, Новоселки вл 11 стр 2", "Чехов 2, Новоселки вл 11 стр 7", "Электросталь"
]

warehouses_split = [
    ["Алматы Атакент", "Астана", "Белые Столбы", "Внуково СГТ", "Волгоград", "Вёшки", "Екатеринбург - Испытателей 14г", "Екатеринбург - Перспективный 12/2", "Казань", "Коледино"],
    ["Котовск", "Краснодар (Тихорецкая)", "Минск", "Невинномысск", "Новосемейкино", "Новосибирск", "Обухово", "Обухово 2", "Обухово СГТ", "Подольск"],
    ["Подольск 3", "Подольск 4", "Пушкино", "Радумля СГТ", "Рязань (Тюшевское)", "СЦ Абакан", "СЦ Абакан 2", "СЦ Артем", "СЦ Архангельск (ул Ленина)", "СЦ Астрахань"],
    ["СЦ Астрахань (Солянка)", "СЦ Байсерке", "СЦ Барнаул", "СЦ Белая Дача", "СЦ Белогорск", "СЦ Бишкек", "СЦ Владикавказ", "СЦ Владимир", "СЦ Внуково", "СЦ Волгоград 2"],
    ["СЦ Вологда", "СЦ Вологда 2", "СЦ Воронеж", "СЦ Иваново", "СЦ Ижевск", "СЦ Иркутск", "СЦ Калуга", "СЦ Кемерово", "СЦ Киров", "СЦ Киров (old)"],
    ["СЦ Крыловская", "СЦ Кузнецк", "СЦ Курск", "СЦ Липецк", "СЦ Махачкала", "СЦ Мурманск", "СЦ Набережные Челны", "СЦ Нижний Новгород", "СЦ Нижний Тагил", "СЦ Новокузнецк"],
    ["СЦ Новосибирск Пасечная", "СЦ Омск", "СЦ Оренбург", "СЦ Ош", "СЦ Пермь 2", "СЦ Псков", "СЦ Пятигорск", "СЦ Пятигорск (Этока)", "СЦ Радумля", "СЦ Ростов-на-Дону"],
    ["СЦ Самара", "СЦ Саратов", "СЦ Семей", "СЦ Серов", "СЦ Симферополь", "СЦ Смоленск 3", "СЦ Сургут", "СЦ Сыктывкар", "СЦ Тамбов", "СЦ Тверь"],
    ["СЦ Томск", "СЦ Тюмень", "СЦ Ульяновск", "СЦ Уральск", "СЦ Уфа", "СЦ Хабаровск", "СЦ Челябинск 2", "СЦ Чита 2", "СЦ Чёрная Грязь", "СЦ Шушары"],
    ["СЦ Шымкент", "СЦ Ярославль", "Санкт-Петербург (Уткина Заводь)", "Сц Брянск 2", "Тула", "Хабаровск", "Чехов 1, Новоселки вл 11 стр 2", "Чехов 2, Новоселки вл 11 стр 7", "Электросталь"],
]

