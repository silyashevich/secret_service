from flask import Flask, render_template, request, session, redirect, url_for
from uuid import uuid4
from sqlite3 import connect, Error
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length


DEBUG = False
app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid4())
WTF_CSRF_ENABLED = True


class SetSecretForm(FlaskForm):
    secret = TextAreaField(label="Information", validators=[InputRequired(), Length(max=4096)])
    submit = SubmitField(label="Generate One-Time Link")


CREATE_TABLE_SECRET = 'CREATE TABLE IF NOT EXISTS `secret` (`token` TEXT, `secret` TEXT );'
INSERT_DATA_SECRET = 'INSERT INTO `secret` (`token`, `secret`) VALUES (?, ?);'
READ_DATA_SECRET = 'SELECT `secret` FROM SECRET WHERE `token` = ?;'
DELETE_DATA_SECRET = 'DELETE FROM `secret` WHERE `token` = ?;'


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
    secret = request.args.get('secret')
    session['token'] = str(uuid4())
    d = {session['token']: secret}
    sqlite_query(INSERT_DATA_SECRET, (session['token'], secret))
    return d


@app.route('/')
def home():
    session['token'] = None
    return render_template("index.html", host_url=request.host_url)


@app.route('/set_secret', methods=['post', 'get'])
def set_secret():
    form = SetSecretForm()
    secret = ''
    if request.method == 'POST':
        secret = request.form.get('secret')
    if form.validate_on_submit():
        secret = form.secret.data
        session['token'] = str(uuid4())
        sqlite_query(INSERT_DATA_SECRET, (session['token'], secret))
        return redirect(url_for('set_secret'))
    return render_template('set_secret.html', form=form, token=session.get('token'), secret=secret, host_url=request.host_url)


@app.route('/get_secret')
def get_secret():
    secret = ''
    session['token'] = request.args.get('token')
    result = sqlite_query(READ_DATA_SECRET, (session['token'],))
    if len(result) > 0:
        secret = result[0][0]
        sqlite_query(DELETE_DATA_SECRET, (session['token'],))
    return render_template('get_secret.html', token=session['token'], secret=secret)


if __name__ == '__main__':
    sqlite_query(CREATE_TABLE_SECRET)
    if DEBUG:
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
