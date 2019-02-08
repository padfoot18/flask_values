from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/admin/')
def admin_page():
    return render_template('index.html')


@app.route('/read/values/')
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


@app.route('/update/values/', methods=['POST', ])
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
            formatted_data = [{"id": data[0][0], "key": data[0][1], "value": data[0][2]}, ]
            resp = jsonify(success=True, data=formatted_data)
        except sqlite3.IntegrityError as e:
            print(e)
            resp = jsonify(success=False, error="Key already exists!")
        finally:
            if connection:
                connection.close()
            return resp


@app.route('/delete/values', methods=['POST', ])
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


if __name__ == '__main__':
    app.run(debug=True)
