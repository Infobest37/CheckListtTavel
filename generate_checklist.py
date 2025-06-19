#generater_checklist
from fpdf import FPDF



class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.set_font("DejaVu", size=14)

    def header(self):
        self.cell(200, 10, txt="Чек-лист для поездки", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=10)
        self.cell(0, 10, "Сгенерировано автоматически", 0, 0, 'C')


def generate_pdf(destination, season, days, trip_type, mode, solo_info=None, family_info=None):
    checklist = ["Паспорт", "Билеты", "Деньги/карты", "Телефон", "Зарядное устройство", "Power bank"]

    def add_common_items():
        checklist.extend([
            "Аптечка (основные лекарства)",
            "Солнцезащитный крем",
            "Влажные салфетки",
            "Бутылка для воды",
            "Ремень безопасности для багажа"
        ])

    def add_hygiene(gender=None):
        hygiene = [
            "Зубная щётка",
            "Зубная паста",
            "Шампунь (мини)",
            "Гель для душа (мини)",
            "Дезодорант",
            "Расческа",
            "Маникюрные ножницы"
        ]
        if gender == "Мужчина":
            hygiene.append("Бритва/станок")
            hygiene.append("Пена для бритья")
        elif gender == "Женщина":
            hygiene.extend([
                "Косметичка",
                "Средства для макияжа",
                "Средства для волос",
                "Средства личной гигиены",
                "Заколки/резинки"
            ])
        checklist.extend(hygiene)

    def add_clothing_by_season_and_trip():
        base_clothing = ["Носки", "Нижнее белье", "Пижама"]

        seasonal = {
            "Лето": [
                "Футболки (2-3 шт)",
                "Шорты/юбки",
                "Легкая обувь",
                "Головной убор",
                "Купальник/плавки",
                "Солнцезащитные очки"
            ],
            "Зима": [
                "Термобелье",
                "Теплые носки",
                "Шапка",
                "Перчатки",
                "Шарф",
                "Утепленная обувь",
                "Теплая куртка"
            ],
            "Осень": [
                "Джинсы/брюки",
                "Куртка",
                "Зонт",
                "Водонепроницаемая обувь"
            ],
            "Весна": [
                "Легкая куртка",
                "Джинсы",
                "Универсальная обувь",
                "Дождевик"
            ]
        }

        trip_specific = {
            "Пляж": [
                "Пляжное полотенце",
                "Сланцы",
                "Солнцезащитный крем SPF 50+",
                "Плавки/купальник (2 шт)"
            ],
            "Горы": [
                "Треккинговые ботинки",
                "Термос",
                "Теплые вещи (даже летом)",
                "Походная аптечка"
            ],
            "Город": [
                "Удобная обувь для ходьбы",
                "Рюкзак/сумка",
                "Путеводитель/карта"
            ],
            "Рабочая": [
                "Деловая одежда",
                "Ноутбук и аксессуары",
                "Блокнот и ручки",
                "Визитки"
            ]
        }

        checklist.extend(base_clothing)
        checklist.extend(seasonal.get(season, []))
        checklist.extend(trip_specific.get(trip_type, []))

    def add_special_by_country():
        country_specific = {
            "Турция": ["Пляжные тапочки", "Адаптер для розеток", "Крем после загара"],
            "Грузия": ["Горная обувь", "Теплые вещи (для гор)", "Лекарства от расстройства желудка"],
            "Индия": ["Антисептик", "Таблетки от желудка", "Влажная туалетная бумага"],
            "Таиланд": ["Спрей от комаров", "Солнцезащитный крем SPF 50+", "Легкая одежда"],
            "ОАЭ": ["Одежда, закрывающая плечи и колени", "Солнцезащитные очки", "Крем от солнца"]
        }

        for country, items in country_specific.items():
            if country.lower() in destination.lower():
                checklist.extend(items)

    def add_solo_items():
        gender = solo_info.get("gender")
        age = int(solo_info.get("age", 0))
        add_hygiene(gender)

        if age < 18:
            checklist.extend([
                "Свидетельство о рождении",
                "Нотариальное согласие родителей",
                "Контактные данные родителей"
            ])
        elif age > 60:
            checklist.extend([
                "Лекарства (полный набор)",
                "Медицинская страховка",
                "Контактные данные родственников"
            ])

    def add_family_items():
        adults = family_info.get("adults", 2)
        children = family_info.get("children", [])

        checklist.append(f"Одежда на {adults} взрослых")
        add_hygiene()

        if children:
            checklist.extend([
                "Документы на детей",
                "Детская аптечка",
                "Детское питание (при необходимости)"
            ])

            for age in children:
                if age < 4:
                    checklist.extend([
                        "Подгузники",
                        "Влажные салфетки детские",
                        "Детская присыпка",
                        "Запасная одежда (2-3 комплекта)",
                        "Игрушки/книжки"
                    ])
                elif age < 12:
                    checklist.extend([
                        "Детский крем от солнца",
                        "Головной убор для ребенка",
                        "Легкая куртка"
                    ])

        if adults + len(children) > 3:
            checklist.extend([
                "Дополнительные зарядные устройства",
                "Больший чемодан",
                "Органайзер для вещей"
            ])

    # Основная логика генерации
    add_common_items()
    add_clothing_by_season_and_trip()
    add_special_by_country()

    if mode == "Один" and solo_info:
        add_solo_items()
    elif mode == "Семья" and family_info:
        add_family_items()

    # Дополнительные пункты в зависимости от длительности
    if days > 7:
        checklist.extend([
            "Дополнительный набор одежды",
            "Стиральный порошок (мини)",
            "Больше гигиенических средств"
        ])
    if days > 14:
        checklist.append("Дополнительная сумка для вещей")

    # Финансы и документы
    checklist.extend([
        "Копии документов (электронные и бумажные)",
        "Страховка",
        "Банковские карты (несколько)",
        "Наличная валюта"
    ])

    # Генерация PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("DejaVu", size=12)

    # Заголовок
    pdf.cell(200, 10, txt=f"Чек-лист для поездки в {destination}", ln=True, align='C')
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Сезон: {season} | Длительность: {days} дней | Тип: {trip_type}", ln=True)
    pdf.cell(200, 10, txt=f"Состав: {mode}", ln=True)
    pdf.ln(10)

    # Список вещей
    pdf.set_font("DejaVu", size=12)
    for i, item in enumerate(checklist, 1):
        pdf.cell(200, 8, txt=f"{i}. ☐ {item}", ln=True)

    filename = f"Travel_Checklist_{destination.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename