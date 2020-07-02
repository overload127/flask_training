import os
import sqlite3

from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    session, abort, g
)


# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'DSFDSFSDFSDFADFASFSDFFSDBGSDGRT43432V42GRV4G'


app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db_.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно не установленно"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    """Закрытие соединение с БД, если оно было установленно"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


menu = [
    {'name': 'Установка', 'url': 'install-flask'},
    {'name': 'Первое приложение', 'url': 'first-app'},
    {'name': 'Обратная связь', 'url': 'contact'}
]


@app.route('/')
@app.route('/index')
def index():
    db = get_db()
    return render_template('index.html', title='Про Flask', menu=menu)


@app.route('/about')
def about():
    return render_template('about.html', title='О сайте', menu=menu)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение успешно отправлено', 'success')
        else:
            flash('Сообщение не было отправлено', 'error')

    return render_template('contact.html', title='Обратная связь', menu=menu)


@app.route('/profile/<username>')
def profile(username):
    if 'userLogger' not in session or username != session['userLogger']:
        abort(401)
    return f'Профиль пользователя: {username}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'userLogger' in session:
        return redirect(url_for('profile', username=session['userLogger']))
    elif (
        request.method == 'POST' and
        request.form['username'] == 'selfedu' and
        request.form['psw'] == '123'
    ):
        session['userLogger'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogger']))

    return render_template('login.html', title='Авторизация', menu=menu)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template(
        'page404.html',
        title='Страница не найдена',
        menu=menu
    )


if __name__ == '__main__':
    app.run()
