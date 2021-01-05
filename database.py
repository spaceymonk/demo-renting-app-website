from ast import literal_eval as make_tuple

import psycopg2 as dbapi2
import datetime
import settings
from user import User


# ---------------------------------------------------------------------------- #
#                               GENERATE METHODS                               #
# ---------------------------------------------------------------------------- #

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


def generate_UserDict(user):
    return {
        'user_id': user[0],
        'email': user[1],
        'passphrase': user[2],
        'real_name': {
            'first_name': user[3].split(',')[0].replace('(', ''),
            'last_name': user[3].split(',')[1].replace(')', '')
        },
        'birthday_date': user[4],
        'sex': user[5],
        'address': user[6],
        'is_banned': user[7],
        'is_admin': user[8],
        'stamp': user[9],
    }


# ---------------------------------------------------------------------------- #
#                                 FETCH METHODS                                #
# ---------------------------------------------------------------------------- #

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


def validate_user(email, password):
    snapshot = []
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_banned, is_admin FROM users WHERE (email=%s) AND (passphrase=%s);", (email, password))
            snapshot = cursor.fetchone()
    if snapshot is not None:
        settings.USERMAP[email] = User(email, password, True, snapshot[0], snapshot[1])
        return settings.USERMAP[email]
    else:
        return None


def fetch_User(email):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
            return generate_UserDict(cursor.fetchone())


def fetch_AllUsers():
    users = []
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY is_banned DESC;")
            for user in cursor.fetchall():
                users.append(generate_UserDict(user))
    return users


# ---------------------------------------------------------------------------- #
#                                UPDATE METHODS                                #
# ---------------------------------------------------------------------------- #

def remove_ban(email):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET is_banned = false WHERE email = %s", (email,))


def add_ban(email):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET is_banned = true WHERE email = %s", (email,))


def remove_user(email):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))


def create_user(user):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                        USERS (EMAIL, PASSPHRASE, REAL_NAME, BIRTHDAY_DATE, SEX, ADDRESS, IS_BANNED, IS_ADMIN, STAMP)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                           (user['email'], user['passphrase'], (user['real_name']['first_name'], user['real_name']['last_name']), user['birthday_date'], user['sex'], user['address'], user['is_banned'], user['is_admin'], user['stamp']))
