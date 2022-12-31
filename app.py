from flask import Flask, render_template, jsonify, url_for, redirect
import requests
import sqlite3


app = Flask(__name__)


def get_db():
    db = sqlite3.connect('mydatabase.db')
    return db


def recreate_table():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DROP TABLE IF EXISTS products")

    cursor.execute(
        "CREATE TABLE products (id INTEGER PRIMARY KEY, productname TEXT UNIQUE, productprice INTEGER UNIQUE, quantity INTEGER)")

    db.commit()
    db.close()


recreate_table()


count = 0


@app.route('/')
@app.route('/home')
def index():

    db = get_db()
    c = db.cursor()

    data = fetchdata()
    unit = []

    for i in range(len(data['result'])):
        unit.append(data['result'][i]['unit_price'])

    res = [eval(i) for i in unit]

    for i in range(len(data['result'])):
        data['result'][i]['unit_price'] = res[i]
    for product in data['result']:
        c.execute('INSERT OR IGNORE INTO products(productname, productprice, quantity) VALUES (?,?,?)',
                  (product['productname'], product['unit_price'], 0))

    c.execute('SELECT * FROM products')
    data_info = c.fetchall()

    db.commit()
    db.close()
    return render_template('index.html', data_info=data_info)


@app.route('/dex_dex')
def dex_dex():
    cart_info = cart()
    return render_template('cart.html', cart_info=cart_info)


@app.route('/increase/<int:id>', methods=['GET', 'POST'])
def increase(id):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE products SET quantity = quantity + 1 WHERE id=?", (id,))
    conn.commit()
    c.execute("SELECT quantity FROM products WHERE id=?", (id,))
    return redirect(url_for('index'))


@app.route('/decrease/<int:id>')
def decrease(id):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE products SET quantity = quantity - 1 WHERE id=? AND quantity > 0", (id,))
    conn.commit()
    c.execute("SELECT quantity FROM products WHERE id=?", (id,))
    return redirect(url_for('index'))
# _______________________________________________________________functions________________________________________________________________


def fetchdata():
    response = requests.get("https://vinayak115.od2.vtiger.com/restapi/vtap/api/shopping%20cart",
                            auth=('vinayak.p+1@vtiger.com', 'MtqNrRCJ2Y55g38T'))
    response = response.json()
    return response


def cart():
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM products')
    c_info = c.fetchall()

    db.commit()
    db.close()
    return (c_info)


if __name__ == '__main__':
    app.run()
