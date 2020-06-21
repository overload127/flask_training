from flask import Flask, url_for, request, render_template, redirect
import time


app = Flask(__name__)


@app.route('/index')
def index():
    return 'Index'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {username}'


@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post {post_id}'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()


def do_the_login():
    return 'Добро пожаловать'


def show_the_login_form():
    return 'Введите логин и пароль'


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/redirect1/')
def show_redirect1():
    time.sleep(1)
    return redirect(url_for('show_redirect2'))


@app.route('/redirect2/')
def show_redirect2():
    time.sleep(1)
    return redirect(url_for('show_redirect1'))


if __name__ == '__main__':
    app.run()
