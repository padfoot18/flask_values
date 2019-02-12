from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, session
from flask_cors import CORS
import sqlite3
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
CORS(app)


# check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print(session['logged_in'])
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' in session:
        if session['logged_in']:
            return redirect('/para/')
    else:
        return render_template('login.html')


@app.route('/key_values/')
@is_logged_in
def admin_page():
    return render_template('key_vals.html', js_files=['key-val.js', ])


@app.route('/read/values/')
@is_logged_in
def read_values():
    formatted_data = []
    try:
        connection = sqlite3.connect('test.db')
        c = connection.cursor()
        c.execute('SELECT * FROM blank_data')
        table_data = c.fetchall()
        for items in table_data:
            formatted_data.append(dict(id=items[0], key=items[1], value=items[2]))
        connection.commit()
        resp = jsonify(formatted_data)
    except Exception as exception:
        print(exception)
        resp = jsonify(success=False)
    finally:
        if connection:
            connection.close()
    return resp


@app.route('/edit_para/', methods=['POST', 'GET'])
@is_logged_in
def edit_para():
    if request.form['str']:
        new_paragraph = request.form['str']
        print(new_paragraph)
    try:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('UPDATE paragraph SET para="' + new_paragraph + '";')
        conn.commit()
        c.execute('select * from paragraph;')
        new_paragraph = c.fetchall()

    except Exception as exception:
        print(exception)

    finally:
        if conn:
            conn.close()

    return new_paragraph


@app.route('/update/values/', methods=['POST', ])
@is_logged_in
def update_values():
    try:
        connection = sqlite3.connect('test.db')
        c = connection.cursor()
        if request.form['id'] and request.form['value']:
            i = request.form['id']
            value = request.form['value']
            sql = 'update blank_data set `value` = "'+value+'" where `id` = "'+i+'";'
            c.execute(sql)
            connection.commit()
            resp = jsonify(success=True, id=i, value=value)
    except Exception as exception:
        print(exception)
        resp = jsonify(success=False)
    finally:
        if connection:
            connection.close()
        return resp


@app.route('/insert/values/', methods=['POST', ])
@is_logged_in
def insert_values():
    if request.form['key'] and request.form['value']:
        key = request.form['key']
        value = request.form['value']
        try:
            connection = sqlite3.connect('test.db')
            c = connection.cursor()
            sql = 'INSERT INTO blank_data (`key`, `value`) VALUES("' + key + '", "' + value + '");'
            c.execute(sql)
            connection.commit()
            sql = 'select * from blank_data where `key` = "'+key+'";'
            c.execute(sql)
            data = c.fetchall()
            formatted_data = {"id": data[0][0], "key": data[0][1], "value": data[0][2]}
            resp = jsonify(success=True, data=formatted_data)
        except sqlite3.IntegrityError as e:
            print(e)
            resp = jsonify(success=False, error="Key already exists!")
        finally:
            if connection:
                connection.close()
        return resp


@app.route('/delete/values', methods=['POST', ])
@is_logged_in
def delete_values():
    if request.form['key']:
        key = request.form['key']

        try:
            connection = sqlite3.connect('test.db')
            c = connection.cursor()
            sql = 'delete from blank_data where `key` = "'+key+'";'
            c.execute(sql)
            connection.commit()
            resp = jsonify(success=True)
        except Exception as e:
            print(e)
            resp = jsonify(success=False)
        finally:
            if connection:
                connection.close()
            return resp


@app.route('/para/')
@is_logged_in
def read_para():
    try:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('select * from paragraph')
        paragraph = c.fetchall()
        conn.commit()
    except sqlite3.IntegrityError:
        return {"error"}
    except Exception as exception:
        print(exception)
    finally:
        if conn:
            conn.close()
    return render_template('view_para.html', para = paragraph[0][0], js_files=['para.js', ])




# register form class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    # username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')


# user register
@app.route('/register', methods=['GET', 'POST'])
@is_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        # username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        try:
            connection = sqlite3.connect('test.db')
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users(name,email,password) VALUES('"+name+"','"+email+"','"+password+"')")
            connection.commit()
            connection.close()
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError as ie:
            print(ie)
        except Exception as e:
            print(e)

    return render_template('register.html', form=form)


# User Login
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        connection = sqlite3.connect('test.db')
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM users WHERE email = '"+email+"'")
        if result.arraysize > 0:
            data = cursor.fetchone()
            password = data[2
            ]
            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('PASSWORD MATCHED')
                session['logged_in'] = True
                session['email'] = email

                flash('You are now logged in', 'success')

                return redirect('/para/')

            else:
                app.logger.info('PASSWORD NOT MATCHED')
                error = 'Incorrect Password'
                return render_template('login.html', error=error)

            cursor.close()
        else:
            app.logger.info('NO USER')
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')





# logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out ', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'ksjbdfljafhbojhbfvoaybfrh'
    app.run(debug=True)
