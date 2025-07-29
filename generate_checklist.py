#generate_checklist.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from data_city import DESTINATION_DATA
import io
from datetime import datetime

# Регистрируем шрифты
pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/DejaVuSans-Bold.ttf'))

# База данных популярных направлений с климатической информацией

def get_destination_info(destination, season):
    """Получаем информацию о направлении и сезоне"""
    for dest in DESTINATION_DATA:
        if dest.lower() in destination.lower():
            return DESTINATION_DATA[dest].get(season, {"temp": "Н/Д", "description": "Нет информации"})
    return {"temp": "Н/Д", "description": "Нет информации"}


def generate_checklist_items(destination, season, days, trip_type, mode, solo_info=None, family_info=None):
    items = {}
    dest_info = get_destination_info(destination, season)

    # Базовые категории
    categories = {
        "Документы": ["Паспорт", "Билеты", "Страховка", "Водительские права", "Бронь отелей"],
        "Электроника": ["Телефон", "Зарядные устройства", "Power bank", "Наушники", "Адаптер для розеток"],
        "Гигиена": ["Зубная щетка", "Зубная паста", "Шампунь", "Гель для душа", "Дезодорант"],
        "Одежда": ["Нижнее белье", "Носки", "Футболки", "Шорты/Брюки", "Пижама"],
        "Аптечка": ["Обезболивающее", "Пластыри", "Антисептик", "Лекарства от аллергии"]
    }

    # Сезонные вещи
    if season == "Зима":
        categories["Одежда"].extend(["Теплая куртка", "Шапка", "Перчатки", "Шарф", "Термобелье"])
        categories["Аптечка"].append("Средство от простуды")
    elif season == "Лето":
        categories["Одежда"].extend(["Шорты", "Футболки", "Головной убор", "Купальник/Плавки"])
        categories["Гигиена"].extend(["Солнцезащитный крем", "Средство после загара"])
        categories["Аптечка"].append("Средство от солнечных ожогов")
    elif season == "Осень":
        categories["Одежда"].extend(["Дождевик", "Зонт", "Ветровка"])
        categories["Аптечка"].append("Средство от простуды")
    elif season == "Весна":
        categories["Одежда"].extend(["Легкая куртка", "Джинсы", "Свитер"])

    # Тип поездки
    if trip_type == "Пляж":
        categories["Аксессуары"] = ["Пляжное полотенце", "Очки для плавания", "Сланцы", "Пляжная сумка"]
    elif trip_type == "Город":
        categories["Одежда"].extend(["Удобная обувь", "Ветровка"])
        categories["Дополнительно"] = ["Карта города", "Путеводитель"]
    elif trip_type == "Горы":
        categories["Одежда"].extend(["Треккинговые ботинки", "Термобелье"])
        categories["Снаряжение"] = ["Рюкзак", "Фонарик", "Термос"]
    elif trip_type == "Рабочая":
        categories["Работа"] = ["Ноутбук", "Блокнот", "Ручки", "Визитки"]

    # Для одного человека
    if mode == "Один" and solo_info:
        gender = solo_info.get("gender")
        age = solo_info.get("age")
        if gender == "Женщина":
            categories["Гигиена"].extend(["Косметика", "Заколки", "Средства для макияжа"])
        if age is not None and age < 18:  # Добавлена проверка на None
            categories["Документы"].append("Согласие родителей на выезд")

    # Для семьи
    if mode == "Семья" and family_info is not None:
        children = family_info.get("children", [])
        if children:  # Только если есть дети
            categories["Для детей"] = []
            for age in children:
                if age < 3:
                    categories["Для детей"].extend(["Подгузники", "Влажные салфетки", "Детское питание"])
                elif age < 10:
                    categories["Для детей"].extend(["Игрушки", "Книжки", "Раскраски"])
    print(f"Debug - mode: {mode}, family_info: {family_info}, solo_info: {solo_info}")
    return categories, dest_info


def generate_pdf(destination, season, days, trip_type, mode, solo_info=None, family_info=None):
    # Получаем данные для чек-листа
    categories, dest_info = generate_checklist_items(destination, season, days, trip_type, mode, solo_info, family_info)
    recommendations = dest_info.get("recommendations", {})

    # Создаем PDF в памяти
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Стили для текста
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='DejaVuSans-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#4361ee')
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontName='DejaVuSans',
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#6c757d')
    )

    # Шапка документа
    title = Paragraph(f"Чек-лист для поездки в {destination}", title_style)
    subtitle_text = f"Сезон: {season} | Температура: {dest_info['temp']} | Длительность: {days} дней"
    subtitle = Paragraph(subtitle_text, subtitle_style)
    desc = Paragraph(f"<i>{dest_info['description']}</i>", subtitle_style)

    # Рисуем шапку
    title.wrapOn(c, width - 40, height)
    title.drawOn(c, 20, height - 40)
    subtitle.wrapOn(c, width - 40, height)
    subtitle.drawOn(c, 20, height - 80)
    desc.wrapOn(c, width - 40, height)
    desc.drawOn(c, 20, height - 110)

    # Начальная позиция для контента
    y_position = height - 150

    # 1. Объединяем "Что взять с собой" из рекомендаций и сгенерированного списка
    if recommendations and 'things_to_take' in recommendations:
        # Добавляем рекомендации "Что взять" в основной список
        if "Одежда" in categories:
            categories["Одежда"].extend(recommendations['things_to_take'])
        else:
            categories["Одежда"] = recommendations['things_to_take']

    # 2. Рисуем основной чек-лист
    for category, items in categories.items():
        # Рисуем название категории
        c.setFont("DejaVuSans-Bold", 14)
        c.setFillColor(colors.HexColor('#3a0ca3'))
        c.drawString(30, y_position, category)
        y_position -= 20

        # Рисуем элементы категории
        c.setFont("DejaVuSans", 11)
        c.setFillColor(colors.black)
        for item in items:
            c.drawString(40, y_position, f"☐ {item}")
            y_position -= 16

            # Проверяем, не вышли ли за пределы страницы
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                c.setFont("DejaVuSans", 12)

    # 3. Добавляем остальные рекомендации (чем заняться, советы, события)
    if recommendations:
        # Отступ перед рекомендациями
        y_position -= 30

        # Стиль для заголовков рекомендаций
        c.setFont("DejaVuSans-Bold", 14)
        c.setFillColor(colors.HexColor('#4361ee'))
        c.drawString(30, y_position, "Дополнительные рекомендации:")
        y_position -= 30

        # Исключаем уже использованные рекомендации "Что взять"
        rec_categories = {k: v for k, v in recommendations.items() if k != 'things_to_take'}

        category_names = {
            'things_to_do': '🏄 Чем заняться',
            'local_tips': '💡 Советы от местных',
            'events': '🎉 События и праздники'
        }

        for cat_key, items in rec_categories.items():
            if not items:
                continue

            # Название категории рекомендаций
            cat_name = category_names.get(cat_key, cat_key)
            c.setFont("DejaVuSans-Bold", 12)
            c.setFillColor(colors.HexColor('#3a0ca3'))
            c.drawString(30, y_position, cat_name)
            y_position -= 20

            # Элементы рекомендаций
            c.setFont("DejaVuSans", 11)
            c.setFillColor(colors.black)
            for item in items:
                c.drawString(40, y_position, f"• {item}")
                y_position -= 16

                if y_position < 50:
                    c.showPage()
                    y_position = height - 50

    # Добавляем подпись в конце
    c.showPage()
    c.setFont("DejaVuSans-Bold", 16)
    c.setFillColor(colors.HexColor('#4361ee'))
    c.drawCentredString(width / 2, height / 2, "Приятного путешествия!")
    c.setFont("DejaVuSans", 12)
    c.drawCentredString(width / 2, height / 2 - 30, "Сгенерировано с помощью TravelCheck")

    c.save()
    buffer.seek(0)
    return buffer.read()