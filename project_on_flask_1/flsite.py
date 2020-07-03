import os
import sqlite3

from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    session, abort, g
)
from werkzeug.security import generate_password_hash

from FDataBase import FDataBase


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


dbase = None


@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Закрытие соединение с БД, если оно было установленно"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/')
def index():
    return render_template(
        'index.html',
        title='Про Flask',
        menu=dbase.getMenu(),
        posts=dbase.getPostAnonce()
    )


@app.route('/about')
def about():
    return render_template('about.html', title='О сайте', menu=dbase.getMenu())


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение успешно отправлено', 'success')
        else:
            flash('Сообщение не было отправлено', 'error')

    return render_template(
        'contact.html',
        title='Обратная связь',
        menu=dbase.getMenu()
    )


@app.route('/profile/<username>')
def profile(username):
    if 'userLogger' not in session or username != session['userLogger']:
        abort(401)
    return f'Профиль пользователя: {username}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if 'userLogger' in session:
    #    return redirect(url_for('profile', username=session['userLogger']))
    # elif (
    if (
        request.method == 'POST' and
        request.form['username'] == 'selfedu' and
        request.form['psw'] == '123'
    ):
        session['userLogger'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogger']))

    return render_template(
        'login.html',
        title='Авторизация',
        menu=dbase.getMenu()
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash_ = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash_)
            if res:
                flash('Вы успешно зарегестрированы', 'success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка при добавлении в БД', 'error')
        else:
            flash('Неверно заполнены поля', 'error')

    return render_template('register.html', menu=dbase.getMenu(), title='Регистрация')


@app.errorhandler(404)
def pageNotFound(error):
    return render_template(
        'page404.html',
        title='Страница не найдена',
        menu=dbase.getMenu()
    )


@app.route('/add_post', methods=['GET', 'POST'])
def addPost():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template(
        'add_post.html',
        menu=dbase.getMenu(),
        title='Добавление статьи'
    )


@app.route('/post/<string:url_post>')
def showPost(url_post):
    title, post = dbase.getPost(url_post)
    if not title:
        abort(404)

    return render_template(
        'post.html',
        menu=dbase.getMenu(),
        title=title,
        post=post
    )


if __name__ == '__main__':
    app.run()
