# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #
from ast import literal_eval as make_tuple
from passlib.hash import pbkdf2_sha256 as hasher
import psycopg2 as dbapi2
import datetime
import settings
from user import User
import base64


# ---------------------------------------------------------------------------- #
#                              APPLICATION RELATED                             #
# ---------------------------------------------------------------------------- #

# ------------------------------- validate_user ------------------------------ #
def validate_user(email, passphrase):
    # Checks whether given email and passphrase is in the database
    snapshot = []
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_banned, is_admin, user_id, passphrase FROM users WHERE email=%s;", (email,))
            snapshot = cursor.fetchone()
    if snapshot is not None:    # user found
        if hasher.verify(passphrase, snapshot[3]):  # check passpharase
            settings.USERMAP[email] = User(email, True, snapshot[0], snapshot[1], snapshot[2])
            return settings.USERMAP[email]
        else:
            return None
    else:
        return None


# ---------------------------------------------------------------------------- #
#                               GENERATE METHODS                               #
# ---------------------------------------------------------------------------- #

# ---------------------------------- PRODUCT --------------------------------- #
def generate_ProductDict_ByTuple(product):
    # returns a dictionary that contains product fields
    try:
        retVal = {
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
                'image': None,
                'stamp': product[9],
            }
        if product[8] is not None:
            retVal['image'] = base64.b64encode(product[8]).decode('utf-8')
        return retVal
    except:
        raise Exception('Product object could not created!')


# ----------------------------------- USER ----------------------------------- #
def generate_UserDict_ByTuple(user):
    # returns a dictionary that contains user fields from a database tuple
    try:
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
            'stamp': user[9]
        }
    except:
        raise Exception('User object could not created!')


# ----------------------------------- ORDER ---------------------------------- #
def generate_OrderDict_ByTuple(order):
    # returns a dictionary that contains order fields from a database tuple
    try:
        return {
            'order_id': order[0],
            'customer': order[1],
            'product_id': order[2],
            'status': order[3],
            'stamp': order[4]
        }
    except:
        raise Exception('Order object could not created!')


# ---------------------------------------------------------------------------- #
#                                 FETCH METHODS                                #
# ---------------------------------------------------------------------------- #


# --------------------------------- PRODUCTS --------------------------------- #
def fetch_Products_ByForm(form):
    # returns a list of products that satisfies given filter form

    try:
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

        # generate statement so far
        statement = """SELECT * FROM products WHERE
                        (status='Active') AND 
                        (price >= %s) AND (price <= %s) AND
                        ((date_interval).begin_date >= %s) AND ((date_interval).end_date <= %s)"""

        # handle category filter
        categories = list(filter(None, [form.get(f"c{x}") for x in settings.CATEGORIES]))
        if len(categories) != 0:
            statement += " AND ("
            for i in range(0, len(categories)-1):
                statement += f" category='{categories[i]}' OR "
            statement += f" category='{categories[-1]}' )"

        # end statement
        statement += ' ORDER BY stamp DESC;'
    except:
        raise Exception('Invalid filter!')

    products = []
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, (min_price, max_price, begin_date, end_date))
            for product in cursor.fetchall():
                products.append(generate_ProductDict_ByTuple(product))

    return products


def fetch_Products_OfUser_ById(id):
    # gets all products from the database which belongs to a certain user
    products = []
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE creator=%s;", (id,))
            for product in cursor.fetchall():
                products.append(generate_ProductDict_ByTuple(product))
    return products


def fetch_Products_All():
    # gets all products from the database which are active
    products = []
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE status='Active';")
            for product in cursor.fetchall():
                products.append(generate_ProductDict_ByTuple(product))
    return products


def fetch_Product_ById(product_id):
    # returns product with the same product_id

    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id=%s;", (product_id,))
            data = cursor.fetchone()
            if data is not None:
                return generate_ProductDict_ByTuple(data)
            else:
                return None


# ----------------------------------- USERS ---------------------------------- #
def fetch_User_ByEmail(email):
    # returns user object where email matches
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s;", (email,))
            data = cursor.fetchone()
            if data is not None:
                return generate_UserDict_ByTuple(data)
            else:
                return None


def fetch_User_ById(id):
    # returns user object where id matches
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id=%s;", (id,))
            data = cursor.fetchone()
            if data is not None:
                return generate_UserDict_ByTuple(data)
            else:
                return None


def fetch_Users_All():
    # returns all users ordered by stamp
    users = []
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY stamp DESC;")
            for user in cursor.fetchall():
                users.append(generate_UserDict_ByTuple(user))
    return users


def get_UserScore_ById(user_id):
    # returns user's total rating by user_id
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT AVG(score) FROM ratings WHERE target=%s;", (user_id,))
            data = cursor.fetchone()
            if data is not None:
                return data[0]
            else:
                return None


# ---------------------------------- ORDERS ---------------------------------- #
def fetch_Order_ById(order_id):
    # returns order object where order_id matches with the argument
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE order_id=%s;", (order_id, ))
            data = cursor.fetchone()
            if data is not None:
                return generate_OrderDict_ByTuple(data)
            else:
                return None


def fetch_Orders_OfUser_ById(user_id):
    # returns all orders that user has involved
    orders = []
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
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
    # returns a dictionary that contains: product title, merchant&customer emails and report, if exists.
    metadata = {}
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
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

            # below stmt fetches report for that order
            cursor.execute("SELECT problem FROM reports WHERE order_id=%s", (order_id,))
            dummy = cursor.fetchone()
            if dummy is not None:
                metadata['problem'] = dummy[0]
    return metadata


# ---------------------------------------------------------------------------- #
#                                UPDATE METHODS                                #
# ---------------------------------------------------------------------------- #


# ----------------------------------- USERS ---------------------------------- #
def update_UserBan_ByEmail(email, banned):
    # banns or unbanns the user by given email
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET is_banned = %s WHERE email = %s", (banned, email))


def update_User_ByEmail(email, fields):
    # update user fields
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET passphrase=%s, real_name=%s, sex=%s, address=%s WHERE email=%s",
                           (fields['passphrase'], (fields['first_name'], fields['last_name']), fields['sex'], fields['address'], email))


# ---------------------------------- PRODUCT --------------------------------- #
def update_ProductStatus_ById(product_id, status):
    # set product's status
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE products SET status=%s WHERE product_id=%s",
                           (status, product_id))


# ----------------------------------- ORDER ---------------------------------- #
def update_OrderStatus_ById(order_id, status):
    # set order's status
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s",
                           (status, order_id))


# ---------------------------------- RATING ---------------------------------- #
def update_Rate(fields):
    # update existing rating entry's score.
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE ratings SET score=%s, stamp=%s WHERE creator=%s AND target=%s;",
                           (fields['score'], fields['stamp'], fields['creator'], fields['target']))

# ---------------------------------------------------------------------------- #
#                                DELETE METHODS                                #
# ---------------------------------------------------------------------------- #


# ----------------------------------- USER ----------------------------------- #
def delete_User_ByEmail(email):
    # remove user from database and all its products, orders etc.
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))


def delete_Product_ById(product_id):
    # remove product from database and all its orders
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))


# ---------------------------------------------------------------------------- #
#                                CREATE METHODS                                #
# ---------------------------------------------------------------------------- #


# ----------------------------------- USERS ---------------------------------- #
def create_User(fields):
    # add a new user entry to database.
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                        users (EMAIL, PASSPHRASE, REAL_NAME, BIRTHDAY_DATE, SEX, ADDRESS, IS_BANNED, IS_ADMIN, STAMP)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                           (fields['email'], fields['passphrase'], (fields['real_name']['first_name'], fields['real_name']['last_name']), fields['birthday_date'], fields['sex'], fields['address'], fields['is_banned'], fields['is_admin'], fields['stamp']))


# --------------------------------- PRODUCTS --------------------------------- #
def create_Product(fields):
    # add a new product entry to database.
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            if fields.get('image') is not None:
                cursor.execute("""INSERT INTO
                        products (CREATOR, STATUS, TITLE, DESCRIPTION, CATEGORY, PRICE, DATE_INTERVAL, IMAGE, STAMP)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                               (fields['creator'], fields['status'], fields['title'], fields['description'], fields['category'], fields['price'], (fields['date_interval']['begin_date'],  fields['date_interval']['end_date']), fields['image'], fields['stamp']))
            else:
                cursor.execute("""INSERT INTO
                        products (CREATOR, STATUS, TITLE, DESCRIPTION, CATEGORY, PRICE, DATE_INTERVAL, STAMP)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                               (fields['creator'], fields['status'], fields['title'], fields['description'], fields['category'], fields['price'], (fields['date_interval']['begin_date'],  fields['date_interval']['end_date']), fields['stamp']))


# ---------------------------------- ORDERS ---------------------------------- #
def create_Order(user_id, product_id):
    # add a new order entry to database.

    # get the product
    product = fetch_Product_ById(product_id)

    # test if avail
    if product['status'] != "Active":
        raise Exception('Product is inactive!')

    # get owner
    owner = fetch_User_ById(product['creator'])

    # if owner itself then raise an error
    if owner['user_id'] == user_id:
        raise Exception("You cannot rent your own item!")

    order_id = None

    # create order
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                                orders (CUSTOMER, PRODUCT_ID, STATUS, STAMP)
                                VALUES (%s, %s, %s, %s) RETURNING order_id;""",
                           (user_id, product_id, "Active", datetime.datetime.now()))
            order_id = cursor.fetchone()

    # preserve product
    update_ProductStatus_ById(product_id, "Rented")

    return order_id[0], owner['email']


# ---------------------------------- RATING ---------------------------------- #
def create_Rate(fields):
    # add a new rating entry to database.
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                        ratings (CREATOR, TARGET, SCORE, STAMP)
                            VALUES (%s, %s, %s, %s);""",
                           (fields['creator'], fields['target'], fields['score'], fields['stamp']))


# ---------------------------------- REPORT ---------------------------------- #
def create_Report(fields):
    # add a new report entry to database.
    with dbapi2.connect(settings.DSN, sslmode='require') as connection:
        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO
                        reports (CREATOR, ORDER_ID, PROBLEM, STAMP)
                            VALUES (%s, %s, %s, %s);""",
                           (fields['creator'], fields['order_id'], fields['problem'], fields['stamp']))
