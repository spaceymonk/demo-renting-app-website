from ast import literal_eval as make_tuple
from passlib.hash import pbkdf2_sha256 as hasher

import psycopg2 as dbapi2
import datetime
import settings
from user import User


def validate_user(email, passphrase):
    snapshot = []
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_banned, is_admin, user_id, passphrase FROM users WHERE email=%s;", (email,))
            snapshot = cursor.fetchone()
    if snapshot is not None:
        if hasher.verify(passphrase, snapshot[3]):
            settings.USERMAP[email] = User(email, True, snapshot[0], snapshot[1], snapshot[2])
            return settings.USERMAP[email]
        else:
            return None
    else:
        return None

# ---------------------------------------------------------------------------- #
#                               GENERATE METHODS                               #
# ---------------------------------------------------------------------------- #


def generate_ProductDict_ByTuple(product):
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


def generate_UserDict_ByTuple(user):
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


def generate_OrderDict_ByTuple(order):
    return {
        'order_id': order[0],
        'customer': order[1],
        'product_id': order[2],
        'status': order[3],
        'stamp': order[4],
    }

# ---------------------------------------------------------------------------- #
#                                 FETCH METHODS                                #
# ---------------------------------------------------------------------------- #

# --------------------------------- PRODUCTS --------------------------------- #


def fetch_Products_ByForm(form):
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
        statement += 'ORDER BY stamp DESC;'
    else:
        statement += f' AND (category = \'{category}\') ORDER BY stamp DESC;'

    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, (min_price, max_price, begin_date, end_date))
            for product in cursor.fetchall():
                products.append(generate_ProductDict_ByTuple(product))

    return products


def fetch_Products_OfUser_ById(id):
    # gets all products from the database

    products = []

    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE creator=%s;", (id,))
            for product in cursor.fetchall():
                products.append(generate_ProductDict_ByTuple(product))

    return products


def fetch_Products_All():
    # gets all products from the database

    products = []

    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE status='Active';")
            for product in cursor.fetchall():
                products.append(generate_ProductDict_ByTuple(product))

    return products


def fetch_Product_ById(product_id):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id=%s;", (product_id,))
            return generate_ProductDict_ByTuple(cursor.fetchone())

# ----------------------------------- USERS ---------------------------------- #


def fetch_User_ByEmail(email):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
            return generate_UserDict_ByTuple(cursor.fetchone())


def fetch_User_ById(id):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id=%s;", (id,))
            return generate_UserDict_ByTuple(cursor.fetchone())


def fetch_Users_All():
    users = []
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY stamp DESC;")
            for user in cursor.fetchall():
                users.append(generate_UserDict_ByTuple(user))
    return users


def get_UserScore_ById(user_id):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT SUM(score) FROM ratings WHERE target=%s;", (user_id,))
            return cursor.fetchone()[0]

# ---------------------------------- ORDERS ---------------------------------- #


def fetch_Orders_OfUser_ById(user_id):
    orders = []
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE customer=%s ORDER BY stamp DESC;", (user_id, ))
            for order in cursor.fetchall():
                orders.append(generate_OrderDict_ByTuple(order))
            cursor.execute("""SELECT orders.* FROM users
	                            INNER JOIN products ON users.user_id=products.creator
	                            INNER JOIN orders ON products.product_id=orders.product_id
	                            WHERE user_id=%s""", (user_id, ))
            for order in cursor.fetchall():
                orders.append(generate_OrderDict_ByTuple(order))
    return orders


def fetch_OrderMetadata_ById(order_id):
    metadata = {}
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            # below stmnt fetches product title and product owner
            cursor.execute("""SELECT title, email FROM users
	                            INNER JOIN products ON users.user_id=products.creator
	                            INNER JOIN orders ON products.product_id=orders.product_id
	                            WHERE order_id=%s""", (order_id, ))
            dummy = cursor.fetchone()
            metadata['product_title'] = dummy[0]
            metadata['merchant'] = dummy[1]
            # below stmt fetches customer email
            cursor.execute("""SELECT email FROM users
	                            INNER JOIN orders ON users.user_id=orders.customer
	                            WHERE order_id=%s""", (order_id, ))
            dummy = cursor.fetchone()
            metadata['customer'] = dummy[0]
    return metadata


# ---------------------------------------------------------------------------- #
#                                UPDATE METHODS                                #
# ---------------------------------------------------------------------------- #

# ----------------------------------- USERS ---------------------------------- #


def update_UserBan_ByEmail(email, banned):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET is_banned = %s WHERE email = %s", (banned, email))


def update_User_ByEmail(email, fields):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET passphrase=%s, real_name=%s, sex=%s, address=%s WHERE email=%s",
                           (fields['passphrase'], (fields['first_name'], fields['last_name']), fields['sex'], fields['address'], email))

# ---------------------------------- PRODUCT --------------------------------- #


def update_ProductStatus_ById(product_id, status):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE products SET status=%s WHERE product_id=%s",
                           (status, product_id))

# ---------------------------------------------------------------------------- #
#                                DELETE METHODS                                #
# ---------------------------------------------------------------------------- #


def delete_User_ByEmail(email):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))


def delete_Product_ById(product_id):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))

# ---------------------------------------------------------------------------- #
#                                CREATE METHODS                                #
# ---------------------------------------------------------------------------- #

# ----------------------------------- USERS ---------------------------------- #


def create_User(user):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                        users (EMAIL, PASSPHRASE, REAL_NAME, BIRTHDAY_DATE, SEX, ADDRESS, IS_BANNED, IS_ADMIN, STAMP)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                           (user['email'], user['passphrase'], (user['real_name']['first_name'], user['real_name']['last_name']), user['birthday_date'], user['sex'], user['address'], user['is_banned'], user['is_admin'], user['stamp']))


# --------------------------------- PRODUCTS --------------------------------- #

def create_Product(fields):
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                        products (CREATOR, STATUS, TITLE, DESCRIPTION, CATEGORY, PRICE, DATE_INTERVAL, STAMP)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                           (fields['creator'], fields['status'], fields['title'], fields['description'], fields['category'], fields['price'], (fields['date_interval']['begin_date'],  fields['date_interval']['end_date']), fields['stamp']))


# ---------------------------------- ORDERS ---------------------------------- #

def create_Order_ById(user_id, product_id):

    # get the product
    product = fetch_Product_ById(product_id)

    # test if avail
    if product['status'] != "Active":
        raise Exception('Product is inactive!')

    # get owner
    owner = fetch_User_ById(product['creator'])

    order_id = None

    # create order
    with dbapi2.connect(settings.DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                                orders (CUSTOMER, PRODUCT_ID, STATUS, STAMP)
                                VALUES (%s, %s, %s, %s) RETURNING order_id;""",
                           (user_id, product_id, "Active", datetime.datetime.now()))
            order_id = cursor.fetchone()

    # preserve product
    update_ProductStatus_ById(product_id, "Rented")

    return order_id[0], owner['email']
