#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cryptography.fernet import Fernet
from datetime import datetime
from flask import json, Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from sqlite3 import connect, Error
from wtforms import TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length
from uuid import uuid4

DEBUG = True
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = str(uuid4())
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
WTF_CSRF_ENABLED = False


class SetSecretForm(FlaskForm):
    secret = TextAreaField(label="Information",
                           validators=[InputRequired(), Length(max=4096)],
                           render_kw={'placeholder': 'Information to be stored in service...'})
    submit = SubmitField(label="Generate a one-time link")


CREATE_TABLE_SECRET = 'CREATE TABLE IF NOT EXISTS `secret` (`uuid` TEXT, `secret` TEXT, `updated` TIMESTAMP );'
INSERT_DATA_SECRET = 'INSERT INTO `secret` (`uuid`, `secret`, `updated`) VALUES (?, ?, ?);'
READ_DATA_SECRET = 'SELECT `secret` FROM SECRET WHERE `uuid` = ?;'
DELETE_DATA_SECRET = 'DELETE FROM `secret` WHERE `uuid` = ?;'


def sqlite_query(query, data=()):
    cnx, records = None, None
    try:
        cnx = connect('db/secret.db')
        cursor = cnx.cursor()
        cursor.execute(query, data)
        records = cursor.fetchall()
        cnx.commit()
    except Error as err:
        print(f'Error: {err}')
    finally:
        if cnx:
            cnx.close()
    return records


@app.route('/make_url')
def make_url():
    pass
    secret_uuid = str(uuid4())
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypt_message = fernet.encrypt(request.args.get('secret').encode())
    link = f'{request.host_url}get_secret?uuid={secret_uuid}&key={key.decode("utf-8")}'
    sqlite_query(INSERT_DATA_SECRET, (secret_uuid, encrypt_message, datetime.now()))
    data = {'uuid': secret_uuid, 'key': key.decode("utf-8"), 'link': link}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/', methods=['GET', 'POST'])
def home():
    set_secret_form = SetSecretForm()
    if set_secret_form.validate_on_submit():
        secret_uuid = str(uuid4())
        key = Fernet.generate_key()
        fernet = Fernet(key)
        encrypt_message = fernet.encrypt(set_secret_form.secret.data.encode())
        link = f'{request.host_url}get_secret?uuid={secret_uuid}&key={key.decode("utf-8")}'
        sqlite_query(INSERT_DATA_SECRET, (secret_uuid, encrypt_message, datetime.now()))
        return redirect(url_for('show_link', link=link))
    return render_template('home.html',
                           form=set_secret_form)


@app.route('/show_link')
def show_link():
    link = {'link': request.args.get('link')}
    return render_template('show_link.html',
                           link=link)


@app.route('/get_secret')
def get_secret():
    secret_uuid = request.args.get('uuid')
    result = sqlite_query(READ_DATA_SECRET, (secret_uuid,))
    if len(result) > 0:
        fernet = Fernet(bytes(request.args.get('key'), 'utf-8'))
        secret = {'secret': fernet.decrypt(result[0][0]).decode()}
        sqlite_query(DELETE_DATA_SECRET, (secret_uuid,))
    else:
        secret = None
    return render_template('get_secret.html',
                           secret=secret)


if __name__ == '__main__':
    sqlite_query(CREATE_TABLE_SECRET)
    if DEBUG:
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
