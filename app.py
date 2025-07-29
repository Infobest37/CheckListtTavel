from flask import Flask, render_template, request, send_from_directory, send_file, redirect, url_for
from generate_checklist import generate_pdf,generate_checklist_items
from io import BytesIO
from data_city import DESTINATION_DATA
import os
import time
from flask_cors import CORS
from flask import send_from_directory

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'temp_pdfs'  # Временная папка для PDF
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Создаем папку для временных файлов
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


# Функция для очистки старых PDF
def clear_old_pdfs(folder, age_seconds=3600):
    now = time.time()
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path) and path.endswith(".pdf"):
            if now - os.path.getmtime(path) > age_seconds:
                os.remove(path)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            print(f"Пользователь указал email: {email}")
        clear_old_pdfs(app.config['UPLOAD_FOLDER'])

        try:
            # Обработка данных для режима "Семья"
            if request.form['mode'] == "Семья":
                adults = request.form.get('adults', '1')
                if not adults.isdigit() or int(adults) < 1:
                    return "Укажите корректное количество взрослых", 400

                children_ages = []
                if request.form.get('has_children') == "Да":
                    if not request.form.get('children_ages'):
                        return "Укажите возраст детей", 400
                    children_ages = [int(a.strip()) for a in request.form['children_ages'].split(',') if a.strip().isdigit()]

            # Обработка данных для режима "Один"
            solo_info = None
            if request.form['mode'] == "Один":
                age = request.form.get('age')
                if age:  # Проверяем, что возраст указан
                    try:
                        age = int(age)  # Преобразуем в число
                    except ValueError:
                        return "Укажите корректный возраст", 400
                solo_info = {
                    "gender": request.form.get("gender"),
                    "age": age  # Теперь это либо число, либо None
                }

            # Генерация PDF
            pdf_data = generate_pdf(
                destination=request.form.get('city') or request.form.get('country'),
                season=request.form['season'],
                days=int(request.form['days']),
                trip_type=request.form['trip_type'],
                mode=request.form['mode'],
                solo_info=solo_info,
                family_info={
                    "adults": int(request.form.get('adults', 1)),
                    "children": children_ages if request.form.get('has_children') == "Да" else []
                } if request.form['mode'] == "Семья" else None
            )

            # Сохраняем временный файл
            filename = f"checklist_{int(time.time())}.pdf"
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(temp_path, 'wb') as f:
                f.write(pdf_data)

            # Перенаправляем на страницу предпросмотра
            return redirect(url_for('preview_pdf',
                                 filename=filename,
                                 destination=request.form.get('city') or request.form.get('country'),
                                 season=request.form['season'],
                                 days=request.form['days'],
                                 trip_type=request.form['trip_type'],
                                 mode=request.form['mode'],
                                 gender=request.form.get('gender'),
                                 age=request.form.get('age'),  # Передаем как строку, преобразуем в preview_pdf
                                 adults=request.form.get('adults'),
                                 has_children=request.form.get('has_children'),
                                 children_ages=request.form.get('children_ages')))

        except Exception as e:
            app.logger.error(f"Error generating PDF: {str(e)}")
            return f"Ошибка сервера: {str(e)}", 500

    return render_template("index.html")


@app.route('/preview/<filename>')
def preview_pdf(filename):
    # Получаем параметры из URL
    destination = request.args.get('destination')
    season = request.args.get('season')
    days = request.args.get('days')
    trip_type = request.args.get('trip_type')
    mode = request.args.get('mode')

    # Обработка параметров для одиночного путешественника
    solo_info = None
    if mode == 'Один':
        age = request.args.get('age')
        if age:  # Проверяем, что возраст указан
            try:
                age = int(age)  # Преобразуем в число
            except ValueError:
                age = None
        solo_info = {
            "gender": request.args.get('gender'),
            "age": age  # Теперь это либо число, либо None
        }

    # Обработка параметров для семейного путешествия
    family_info = None
    if mode == 'Семья':
        children_ages = []
        if request.args.get('has_children') == 'Да':
            children_ages_str = request.args.get('children_ages', '')
            children_ages = [int(a.strip()) for a in children_ages_str.split(',') if a.strip().isdigit()]

        family_info = {
            "adults": int(request.args.get('adults', 1)),
            "children": children_ages
        }

    # Генерация данных чек-листа
    categories, dest_info = generate_checklist_items(
        destination=destination,
        season=season,
        days=int(days) if days else 7,
        trip_type=trip_type,
        mode=mode,
        solo_info=solo_info,
        family_info=family_info
    )

    # Формируем данные для шаблона
    checklist_data = {
        "destination": destination,
        "season": f"{season} ({dest_info['temp']})",
        "description": dest_info["description"],
        "categories": categories,
        "recommendations": dest_info.get("recommendations", {})
    }

    return render_template('preview.html', checklist_data=checklist_data, pdf_filename=filename)
@app.route('/pdf/<filename>')
def serve_pdf(filename):
    # Отдаем PDF для просмотра в iframe
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/download/<filename>')
def download_pdf(filename):
    # Отдаем PDF для скачивания
    response = send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True,
        download_name='travel_checklist.pdf'
    )

    # Удаляем временный файл после скачивания
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except:
        pass

    return response


@app.route('/print/<filename>')
def print_pdf(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "Файл не найден или был удалён", 404

    return send_file(
        file_path,
        mimetype='application/pdf',
        download_name=filename,
        as_attachment=False  # Важно для открытия в браузере
    )


@app.route('/yandex_4b1e491e902157f6.html')
def yandex_verification():
    return send_from_directory('.', 'yandex_4b1e491e902157f6.html')
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)