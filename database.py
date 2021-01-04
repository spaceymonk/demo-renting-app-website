from ast import literal_eval as make_tuple

import psycopg2 as dbapi2
import datetime
import settings
from user import User


def fetch_FilteredProducts(form):
    products = []

    # handle price filter
    min_price = 0
    max_price = 999999
    if form.get('min-price') != "":
        min_price = int(form.get('min-price'))
    if form.get('max-price') != "":
        max_price = int(form.get('max-price'))
    if min_price > max_price:
        min_price, max_price = max_price, min_price

    # handle date filter
    begin_date = datetime.datetime(2000, 1, 1)
    end_date = datetime.datetime(2200, 1, 1)
    if form.get('datepick-begin') != "":
        begin_date = datetime.datetime.strptime(form.get('datepick-begin'), "%Y-%m-%d")
    if form.get('datepick-end') != "":
        end_date = datetime.datetime.strptime(form.get('datepick-end'), "%Y-%m-%d")
    if begin_date > end_date:
        begin_date, end_date = end_date, begin_date

    # generate statement
    statement = """SELECT * FROM products WHERE
                    (price >= %s) AND (price <= %s) AND
                    ((date_interval).begin_date >= %s) AND ((date_interval).end_date <= %s)"""

    # handle category filter
    category = form.get('category')

    if category == 'All':
        statement += ';'
    else:
        statement += f' AND (category = \'{category}\')'

    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, (min_price, max_price, begin_date, end_date))
            for product in cursor.fetchall():
                products.append(generate_ProductDict(product))

    return products


def fetch_AllProducts():
    # gets all products from the database

    products = []

    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products;")
            for product in cursor.fetchall():
                products.append(generate_ProductDict(product))

    return products


def generate_ProductDict(product):
    # returns a dictionary that contains product fields
    return {
        'product_id': product[0],
        'creator': product[1],
        'status': product[2],
        'title': product[3],
        'description': product[4],
        'category': product[5],
        'price': product[6],
        'date_interval': {
            'begin_date': datetime.datetime.strptime(product[7].split(',')[0], "(%Y-%m-%d"),
            'end_date': datetime.datetime.strptime(product[7].split(',')[1], "%Y-%m-%d)"),
        },
        'stamp': product[8],
    }


def fetch_user(email, password):
    snapshot = []
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_banned, is_admin FROM users WHERE (email=%s) AND (passphrase=%s)", (email, password))
            snapshot = cursor.fetchone()
    if snapshot is not None:
        settings.USERMAP[email] = User(email, password, True, snapshot[0])
        return settings.USERMAP[email]
    else:
        return None
