from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g

import sqlite3


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


def login_admin():
    session['admin_logged'] = 1


def isLogged():
    return True if session.get('admin_logged') else False


def logout_admin():
    session.pop('admin_logged', None)


menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listpubs', 'title': 'Список статей'},
        {'url': '.logout', 'title': 'Выйти'}]


@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    db = g.get('link_db')


@admin.teardown_request
def teaedown_request(request):
    global db
    db = None
    return request


@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))
    
    return render_template('admin/index.html', menu=menu, title='Админ-панель')


@admin.route('/login', methods=['POST', 'GET'])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['psw'] == '12345':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash('Неверная пара логин/пароль', 'error')

    return render_template('admin/login.html', title='Админ-панель')


@admin.route('/logout', methods=['GET', 'POST'])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))


@admin.route('/list-pubs')
def listpubs():
    if not isLogged():
        return redirect(url_for('.login'))

    post_list=[]
    if db:
        try:
            cur = db.cursor()
            cur.execute(f'SELECT title, text, url FROM posts')
            post_list = cur.fetchall()
        except sqlite3.Error as e:
            print(f'Ошибка получения статей из БД {e}')

    return render_template('admin/listpubs.html', title='Список статей', menu=menu, post_list=post_list)


@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    user_list=[]
    if db:
        try:
            cur = db.cursor()
            cur.execute(f'SELECT name, email FROM users ORDER BY time DESC')
            user_list = cur.fetchall()
        except sqlite3.Error as e:
            print(f'Ошибка получения статей из БД {e}')

    return render_template('admin/listusers.html', title='Список пользователей', menu=menu, user_list=user_list)
