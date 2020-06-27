from flask import Flask, request, render_template


app = Flask(__name__)


@app.route('/hello_world/')
def hello_world():

    return '<h1>Hello World!</h1>'


@app.route('/firt_get/')
def firt_get():

    return f'<h1>Hello {request.args["lastname"]} {request.args["name"]}</h1>'


@app.route('/template/')
def template():

    return render_template('index.html', name='Kostya', lastname='Vin')


@app.route('/template_get/')
def template_get():

    return render_template(
        'index.html',
        name=request.args['name'],
        lastname=request.args['lastname']
    )


if __name__ == '__main__':
    app.run()
