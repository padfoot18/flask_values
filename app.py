from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/admin')
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
    except Exception as exception:
        print(exception)
    finally:
        if connection:
            connection.close()
    return jsonify(formatted_data)


@app.route('/update/values/', methods=['POST', 'GET'])
def update_values():
    try:
        connection = sqlite3.connect('test.db')
        c = connection.cursor()
        id = request.form['id']
        value = request.form['value']
        sql = 'update blank_data set `value` = "'+value+'" where `id` = "'+id+'";'
        print(sql)
        c.execute(sql)
        connection.commit()
    except Exception as exception:
        print(exception)
    finally:
        if connection:
            connection.close()
    return jsonify(success=True, id=id, value=value)


if __name__ == '__main__':
    app.run(debug=True)
