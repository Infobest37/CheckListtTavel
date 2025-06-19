#app
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from generate_checklist import generate_pdf

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Необходимо для работы flash-сообщений

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            mode = request.form["mode"]
            destination = request.form["destination"]
            season = request.form["season"]
            days = int(request.form["days"])
            trip_type = request.form["trip_type"]

            if mode == "Один":
                gender = request.form["gender"]
                age_str = request.form.get("age", "0")  # Получаем возраст как строку, по умолчанию "0"
                age = int(age_str) if age_str.strip() else 0  # Преобразуем в число, если не пусто
                filename = generate_pdf(destination, season, days, trip_type, mode,
                                     solo_info={"gender": gender, "age": age})

            else:  # mode == "Семья"
                adults = int(request.form["adults"])
                has_children = request.form["has_children"]
                children_ages = []
                if has_children == "Да":
                    children_ages_str = request.form.get("children_ages", "")
                    children_ages = [int(a.strip()) for a in children_ages_str.split(',') if a.strip().isdigit()]
                filename = generate_pdf(destination, season, days, trip_type, mode,
                                     family_info={"adults": adults, "children": children_ages})

            return send_file(filename, as_attachment=True)

        except ValueError as e:
            flash(f"Ошибка ввода данных: {str(e)}", "error")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Произошла ошибка: {str(e)}", "error")
            return redirect(url_for('index'))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)