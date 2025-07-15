from flask import Flask, render_template, request, send_from_directory, send_file, redirect, url_for
from generate_checklist import generate_pdf
from io import BytesIO
import os
import time
from flask_cors import CORS

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

            if request.form['mode'] == "Семья":
                adults = request.form.get('adults', '1')
                if not adults.isdigit() or int(adults) < 1:
                    return "Укажите корректное количество взрослых", 400

                children_ages = []
                if request.form.get('has_children') == "Да":
                    if not request.form.get('children_ages'):
                        return "Укажите возраст детей", 400
                    children_ages = [int(a.strip()) for a in request.form['children_ages'].split(',') if
                                     a.strip().isdigit()]

            # Генерация PDF
            pdf_data = generate_pdf(
                destination=request.form.get('city') or request.form.get('country'),
                season=request.form['season'],
                days=int(request.form['days']),
                trip_type=request.form['trip_type'],
                mode=request.form['mode'],
                solo_info={
                    "gender": request.form.get("gender"),
                    "age": int(request.form.get("age", 0)) if request.form.get("age") else None
                } if request.form['mode'] == "Один" else None,
                family_info={
                    "adults": int(request.form.get("adults", 1)),
                    "children": children_ages if request.form.get('has_children') == "Да" else []
                } if request.form['mode'] == "Семья" else None
            )

            # Сохраняем временный файл для предпросмотра
            filename = f"checklist_{int(time.time())}.pdf"
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(temp_path, 'wb') as f:
                f.write(pdf_data)

            # Перенаправляем на страницу предпросмотра
            return redirect(url_for('preview_pdf', filename=filename))


        except Exception as e:
            app.logger.error(f"Error generating PDF: {str(e)}")
            return f"Ошибка сервера: {str(e)}", 500


    return render_template("index.html")


@app.route('/preview/<filename>')
def preview_pdf(filename):
    return render_template('preview.html', filename=filename)


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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)