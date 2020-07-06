import os
import sqlite3

from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    session, abort, g, make_response
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from FDataBase import FDataBase
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin


# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'DSFDSFSDFSDFADFASFSDFFSDBGSDGRT43432V42GRV4G'
MAX_CONTENT_LENGHT = 1024 * 1024


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.register_blueprint(admin, url_prefix='/admin')


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', menu=dbase.getMenu(), title='Профиль')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Неверная пара логин/пароль', 'error')

    return render_template('login.html', menu=dbase.getMenu(), title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_ = generate_password_hash(request.form['psw'])
        res = dbase.addUser(request.form['name'], request.form['email'], hash_)
        if res:
            flash('Вы успешно зарегестрированы', 'success')
            return redirect(url_for('login'))
        else:
            flash('Ошибка при добавлении в БД', 'error')

    return render_template('register.html', menu=dbase.getMenu(), title='Регистрация', form=form)


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
@login_required
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


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ''

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash('Ошибка обновления аватара', 'error')
                flash('Аватар обновлен', 'success')
            except FileNotFoundError as e:
                flash('Ошибка чтения файла', 'error')
        else:
            flash('Ошибка обновления аватара', 'error')

    return redirect(url_for('profile'))
                


if __name__ == '__main__':
    app.run()
