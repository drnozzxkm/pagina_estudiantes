from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import json
from pathlib import Path

BASE = Path(__file__).parent
DATA_DIR = BASE / 'data'
USERS_FILE = DATA_DIR / 'users.json'
COURSES_FILE = DATA_DIR / 'courses.json'

app = Flask(__name__)
# en producción cambia esto por una variable de entorno segura
app.secret_key = 'CAMBIA_ESTA_SECRETA_POR_ALGO_SEGURA'

# Helpers para leer y escribir JSON
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_json(path):
    if not path.exists():
        if path.name == 'users.json':
            default = {'users': []}
        else:
            default = {'courses': []}
        write_json(path, default)
        return default
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            if path.name == 'users.json':
                default = {'users': []}
            else:
                default = {'courses': []}
            write_json(path, default)
            return default

# Rutas de autenticación
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('main'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        if not username or not password:
            flash('Nombre y contraseña requeridos')
            return redirect(url_for('register'))

        users_data = read_json(USERS_FILE)
        users = users_data.get('users', [])

        if any(u.get('username','').lower() == username.lower() for u in users):
            flash('Usuario ya existe')
            return redirect(url_for('register'))

        hashed = generate_password_hash(password)
        users.append({'username': username, 'password': hashed})
        users_data['users'] = users
        write_json(USERS_FILE, users_data)
        flash('Registrado correctamente, inicia sesión')
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = (request.form.get('username') or '').strip()
    password = request.form.get('password') or ''

    if not username or not password:
        flash('Nombre y contraseña requeridos')
        return redirect(url_for('home'))

    users_data = read_json(USERS_FILE)
    users = users_data.get('users', [])
    user = next((u for u in users if u.get('username','').lower() == username.lower()), None)

    if not user:
        flash('Usuario o contraseña incorrectos')
        return redirect(url_for('home'))

    stored_pw = user.get('password', '')
    try:
        valid = check_password_hash(stored_pw, password)
    except Exception:
        valid = False

    if not valid:
        flash('Usuario o contraseña incorrectos')
        return redirect(url_for('home'))

    session['user'] = username
    return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# API y vistas principales
@app.route('/main')
def main():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('main.html', user=session.get('user'))

@app.route('/api/courses')
def api_courses():
    courses = read_json(COURSES_FILE)
    return jsonify(courses.get('courses', []))

@app.route('/api/topics/<course_slug>')
def api_topics(course_slug):
    courses = read_json(COURSES_FILE)
    course = next((c for c in courses.get('courses', []) if c.get('slug') == course_slug), None)
    if not course:
        return jsonify([])
    return jsonify(course.get('topics', []))

@app.route('/topic/<course_slug>/<topic_slug>')
def topic_page(course_slug, topic_slug):
    courses = read_json(COURSES_FILE)
    course = next((c for c in courses.get('courses', []) if c.get('slug') == course_slug), None)
    if not course:
        return 'Curso no encontrado', 404

    topic = next((t for t in course.get('topics', []) if t.get('slug') == topic_slug), None)
    if not topic:
        return 'Tema no encontrado', 404

    contenido = (topic.get('contenido', '') or '').strip()


    if contenido.lower().endswith('.html'):
        return render_template(contenido, course=course, topic=topic)
    return render_template('topic.html', course=course, topic=topic, contenido=contenido)



@app.route('/quiz/<course_slug>/<topic_slug>')
def quiz_page(course_slug, topic_slug):
    courses = read_json(COURSES_FILE)
    course = next((c for c in courses.get('courses', []) if c.get('slug') == course_slug), None)
    if not course:
        return "Curso no encontrado", 404
    topic = next((t for t in course.get('topics', []) if t.get('slug') == topic_slug), None)
    if not topic:
        return "Tema no encontrado", 404

    quiz = topic.get("quiz", [])
    return render_template("quiz.html", course=course, topic=topic, quiz=quiz)

@app.route('/quiz_result/<course_slug>/<topic_slug>', methods=['POST'])
def quiz_result(course_slug, topic_slug):
    correct = int(request.form.get('correctCount', 0))
    total = int(request.form.get('totalQuestions', 0))

    # Mensaje según rendimiento
    if correct == total:
        message = "¡Perfecto! Dominaste este tema. 🏆"
    elif correct >= total * 0.7:
        message = "Muy bien, casi perfecto. Sigue practicando. 💪"
    elif correct >= total * 0.4:
        message = "Vas por buen camino, pero necesitas reforzar algunos puntos. 📘"
    else:
        message = "Necesitas repasar el tema con calma. Tú puedes mejorar. 🌱"

    return render_template(
        "quiz_result.html",
        correct=correct,
        total=total,
        message=message,
        course_slug=course_slug,
        topic_slug=topic_slug
    )



if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



