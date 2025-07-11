#app
from flask import Flask, render_template, request,  redirect, url_for, send_from_directory, make_response, jsonify
from generate_checklist import generate_pdf
import os
import time
from data_city import DESTINATION_DATA, Cities  # Импортируем данные

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'temp_pdfs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


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
        clear_old_pdfs(app.config['UPLOAD_FOLDER'])
    if request.method == "POST":
        try:
            # Проверяем обязательные поля
            required_fields = ['mode', 'season', 'days', 'trip_type']
            for field in required_fields:
                if field not in request.form:
                    return "Не заполнены обязательные поля", 400

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
                    "children": [
                        int(a.strip()) for a in request.form.get("children_ages", "").split(',')
                        if a.strip().isdigit()
                    ] if request.form.get("has_children") == "Да" else []
                } if request.form['mode'] == "Семья" else None
            )

            filename = f"checklist_{int(time.time())}.pdf"
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            with open(temp_path, 'wb') as f:
                f.write(pdf_data)

            return redirect(url_for('preview_pdf', filename=filename))

        except Exception as e:
            return f"Ошибка сервера: {str(e)}", 500

    return render_template("index.html")


@app.route('/preview/<filename>')
def preview_pdf(filename):
    return render_template('preview.html', filename=filename)


@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/download/<filename>')
def download_pdf(filename):
    response = send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    # Удаляем временный файл после отправки
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except:
        pass
    return response


@app.route('/print/<filename>')
def print_pdf(filename):
    response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], filename))
    response.headers['Content-Disposition'] = 'inline; filename="checklist.pdf"'
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)