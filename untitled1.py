import os,re
import sqlite3
from flask import Flask, request, g, redirect, url_for, abort, \
    render_template, flash, session, jsonify, Response
from flask.ext.triangle import Triangle
import json
# configuration
DATABASE = '/tmp/flasker.db'
DEBUG = True
SECRET_KEY = 'developement key'
USERNAME = 'admin'
PASSWORD = 'default'

productData = [{ "name": "Apples", "category": "Fruit", "price": 1.20, "expiry": 10 },
{ "name": "Bananas", "category": "Fruit", "price": 2.42, "expiry": 7 },
{ "name": "Pears", "category": "Fruit", "price": 2.02, "expiry": 6 },
{ "name": "Tuna", "category": "Fish", "price": 20.45, "expiry": 3 },
{ "name": "Salmon", "category": "Fish", "price": 17.93, "expiry": 2 },
{ "name": "Trout", "category": "Fish", "price": 12.93, "expiry": 4 }]

json_data = '{ "name": "Apples", "category": "Fruit", "price": 1.20, "expiry": 10 }'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# init database
from contextlib import closing
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    tem_list = ['hello']
    for i in entries:
        if i['title'] == 'data':
            data_list = [int(i) for i in re.split('[^\d]', i['text'])]
            tem_list.append(data_list)
    return render_template("show_entries.html", entries=entries, data=tem_list[0])

@app.route('/ang' ,methods=['GET', 'POST'])
def show_angular():
    return render_template('index.html')


@app.route('/productData.json' ,methods=['GET', 'POST'])
def show_ajax():
    response = json.dumps(productData)
    resp = Response(response=response,
    status=200,
    mimetype="application/json")
    return (resp)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    print request
    print type(request)
    if request.method == 'POST':
        print request.form
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)




@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
