from fpdf import FPDF
from typing import List, Dict, Optional


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.set_font("DejaVu", size=14)

    def header(self):
        self.cell(200, 10, txt="Умный чек-лист для путешествия", ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", size=8)
        self.cell(0, 10, "Сгенерировано TravelCheck Pro", 0, 0, 'C')


def generate_pdf(destination: str, season: str, days: int, trip_type: str,
                 mode: str, solo_info: Optional[Dict] = None,
                 family_info: Optional[Dict] = None) -> str:
    # Основные категории
    checklist = {
        'documents': [],
        'clothes': [],
        'hygiene': [],
        'electronics': [],
        'medicine': [],
        'special': [],
        'children': [],
        'other': []
    }

    # 1. Базовые документы и вещи
    checklist['documents'].extend([
        "Паспорт (+копия)",
        "Билеты (электронные/бумажные)",
        "Страховка",
        "Водительские права (если нужно)",
        "Бронь отелей/аренды"
    ])

    checklist['electronics'].extend([
        "Телефон + зарядка",
        "Power bank",
        "Универсальный адаптер для розеток",
        "Наушники"
    ])

    # 2. Логика для разных типов стран
    def add_country_specific_items():
        # Классификация стран
        muslim_countries = ["ОАЭ", "Турция", "Египет", "Катар"]
        asian_countries = ["Таиланд", "Индия", "Вьетнам", "Китай"]
        cold_countries = ["Финляндия", "Норвегия", "Исландия", "Канада"]

        # Жаркие страны
        if any(c.lower() in destination.lower() for c in muslim_countries + asian_countries):
            checklist['special'].extend([
                "Солнцезащитный крем SPF 50+",
                "Солнцезащитные очки",
                "Головной убор"
            ])

        # Мусульманские страны
        if any(c.lower() in destination.lower() for c in muslim_countries):
            checklist['clothes'].extend([
                "Одежда, закрывающая плечи и колени (для женщин)",
                "Пляжная одежда (скромная)"
            ])

        # Азиатские страны
        if any(c.lower() in destination.lower() for c in asian_countries):
            checklist['medicine'].extend([
                "Активированный уголь",
                "Средство от расстройства желудка",
                "Репеллент от комаров"
            ])
            checklist['hygiene'].append("Влажная туалетная бумага")

        # Холодные страны
        if any(c.lower() in destination.lower() for c in cold_countries):
            checklist['clothes'].extend([
                "Термобелье",
                "Теплые носки (2-3 пары)",
                "Шапка/перчатки"
            ])

    # 3. Логика для сезона и типа поездки
    def add_seasonal_items():
        seasonal_clothes = {
            "Лето": [
                "Футболки (3-5 шт)",
                "Шорты/юбки",
                "Легкая обувь",
                "Купальник/плавки (2 шт)"
            ],
            "Зима": [
                "Теплая куртка",
                "Шарф",
                "Утепленные ботинки",
                "Термобелье"
            ],
            "Весна/Осень": [
                "Дождевик/зонт",
                "Ветровка",
                "Универсальная обувь"
            ]
        }

        trip_specific = {
            "Пляж": [
                "Пляжное полотенце",
                "Сланцы",
                "Водонепроницаемый чехол для телефона"
            ],
            "Горы": [
                "Треккинговые ботинки",
                "Термос",
                "Походная аптечка"
            ],
            "Город": [
                "Удобная обувь для ходьбы",
                "Городской рюкзак",
                "Путеводитель"
            ]
        }

        # Выбираем сезон
        season_key = "Лето" if season == "Лето" else "Зима" if season == "Зима" else "Весна/Осень"
        checklist['clothes'].extend(seasonal_clothes.get(season_key, []))

        # Добавляем специфичные для поездки вещи
        checklist['clothes'].extend(trip_specific.get(trip_type, []))

    # 4. Логика для пола и возраста
    def add_personal_items():
        if mode == "Один" and solo_info:
            gender = solo_info.get("gender")
            age = solo_info.get("age", 25)

            # Гигиена по полу
            if gender == "Мужчина":
                checklist['hygiene'].extend([
                    "Бритва/станок",
                    "Пена для бритья",
                    "Мужской дезодорант"
                ])
            elif gender == "Женщина":
                checklist['hygiene'].extend([
                    "Косметичка",
                    "Средства гигиены",
                    "Заколки/резинки"
                ])

            # Возрастные особенности
            if age < 18:
                checklist['documents'].append("Согласие родителей")
            elif age > 60:
                checklist['medicine'].extend([
                    "Все необходимые лекарства",
                    "Медицинская карта (копия)"
                ])

    # 5. Логика для семьи с детьми
    def add_family_items():
        if mode == "Семья" and family_info:
            adults = family_info.get("adults", 2)
            children_ages = family_info.get("children", [])

            # Для взрослых
            checklist['hygiene'].extend([
                "Гигиенические принадлежности (x{})".format(adults),
                "Полотенца (x{})".format(adults)
            ])

            # Для детей
            for age in children_ages:
                if age < 2:  # Младенцы
                    checklist['children'].extend([
                        "Подгузники (запас)",
                        "Детское питание",
                        "Соски/бутылочки",
                        "Крем под подгузник"
                    ])
                elif age < 6:  # Дошкольники
                    checklist['children'].extend([
                        "Любимая игрушка",
                        "Детская посуда",
                        "Влажные салфетки"
                    ])
                else:  # Школьники/подростки
                    checklist['children'].append("Развлечения для ребенка")

    # 6. Логика для длительности поездки
    def adjust_for_duration():
        if days <= 3:  # Короткая поездка
            checklist['clothes'] = [item.replace("(3-5 шт)", "(2-3 шт)")
                                    for item in checklist['clothes']]
        elif days > 14:  # Длительная поездка
            checklist['other'].extend([
                "Стиральный порошок (мини)",
                "Дополнительная сумка",
                "Больше гигиенических средств"
            ])

    # 7. Дополнительные умные советы
    def add_smart_tips():
        if days > 7:
            checklist['other'].append("Зарядка для устройств (удвоенное количество)")

        if "пляж" in trip_type.lower():
            checklist['special'].append("Водонепроницаемый чехол для документов")

    # Собираем все вместе
    add_country_specific_items()
    add_seasonal_items()
    add_personal_items()
    add_family_items()
    adjust_for_duration()
    add_smart_tips()

    # Генерация PDF
    pdf = PDF()
    pdf.add_page()

    # Заголовок
    pdf.set_font("DejaVu", size=16)
    pdf.cell(200, 10, txt=f"Умный чек-лист: {destination}", ln=True, align='C')
    pdf.ln(5)

    # Мета-информация
    pdf.set_font("DejaVu", size=12)
    pdf.cell(200, 8, txt=f"▸ Сезон: {season} ▸ Дней: {days} ▸ Тип: {trip_type}", ln=True)
    pdf.cell(200, 8, txt=f"▸ Путешественники: {get_travelers_description(mode, solo_info, family_info)}", ln=True)
    pdf.ln(10)

    # Список вещей по категориям
    pdf.set_font("DejaVu", size=12)

    for category, items in checklist.items():
        if items:  # Только непустые категории
            pdf.set_font("DejaVu", size=12, style='B')
            pdf.cell(200, 8, txt=f"{get_category_name(category)}:", ln=True)
            pdf.set_font("DejaVu", size=10)

            for i, item in enumerate(items, 1):
                pdf.cell(200, 7, txt=f"  {i}. ☐ {item}", ln=True)
            pdf.ln(5)

    filename = f"Travel_Checklist_{destination.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename


def get_travelers_description(mode: str, solo_info: Optional[Dict], family_info: Optional[Dict]) -> str:
    if mode == "Один" and solo_info:
        gender = solo_info.get("gender", "")
        age = solo_info.get("age", "")
        return f"{gender}, {age} лет"
    elif mode == "Семья" and family_info:
        adults = family_info.get("adults", 2)
        children = family_info.get("children", [])
        return f"{adults} взрослых + {len(children)} детей"
    return ""


def get_category_name(category: str) -> str:
    names = {
        'documents': '📄 Документы',
        'clothes': '👕 Одежда',
        'hygiene': '🧴 Гигиена',
        'electronics': '📱 Электроника',
        'medicine': '💊 Аптечка',
        'special': '🌟 Специальные вещи',
        'children': '🧸 Для детей',
        'other': '📦 Прочее'
    }
    return names.get(category, category.capitalize())