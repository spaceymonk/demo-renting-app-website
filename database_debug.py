from utility import *
from passlib.hash import pbkdf2_sha256 as hasher
import datetime


def initDatabase(connection):
    # Clears database then
    # creates tables, constraints etc.
    statement = """
    DROP TABLE IF EXISTS USERS CASCADE;
    DROP TABLE IF EXISTS ORDERS CASCADE;
    DROP TABLE IF EXISTS PRODUCTS CASCADE;
    DROP TABLE IF EXISTS RATINGS CASCADE;
    DROP TABLE IF EXISTS REPORTS CASCADE;
    DROP TYPE IF EXISTS DATE_INTERVALS CASCADE;
    DROP TYPE IF EXISTS FULL_NAME CASCADE;

    CREATE TYPE FULL_NAME AS (
        FIRST_NAME VARCHAR(255),
        LAST_NAME VARCHAR(255)
    );

    CREATE TYPE DATE_INTERVALS AS (
        BEGIN_DATE DATE,
        END_DATE DATE
    );

    CREATE TABLE USERS(
        USER_ID SERIAL PRIMARY KEY,
        EMAIL VARCHAR(255) UNIQUE NOT NULL,
        PASSPHRASE VARCHAR(255) NOT NULL CHECK(LENGTH(PASSPHRASE) >= 5),
        REAL_NAME FULL_NAME NOT NULL,
        BIRTHDAY_DATE DATE NOT NULL,
        SEX CHAR(1) NOT NULL,
        ADDRESS VARCHAR(255),
        IS_BANNED BOOLEAN NOT NULL,
        IS_ADMIN BOOLEAN NOT NULL,
        STAMP DATE NOT NULL CHECK(STAMP > BIRTHDAY_DATE)
    );

    CREATE TABLE PRODUCTS(
        PRODUCT_ID SERIAL PRIMARY KEY,
        CREATOR INTEGER NOT NULL,
        STATUS VARCHAR(255) NOT NULL,
        TITLE VARCHAR(255) NOT NULL,
        DESCRIPTION VARCHAR(255) NOT NULL,
        CATEGORY VARCHAR(255) NOT NULL,
        PRICE NUMERIC NOT NULL CHECK(PRICE > 0),
        DATE_INTERVAL DATE_INTERVALS NOT NULL,
        STAMP DATE NOT NULL,
        CONSTRAINT FK_CREATOR FOREIGN KEY (CREATOR) REFERENCES USERS(USER_ID)
    );

    CREATE TABLE RATINGS(
        CREATOR INTEGER NOT NULL,
        TARGET INTEGER NOT NULL,
        SCORE INTEGER NOT NULL CHECK(SCORE <= 10 AND SCORE >= 0),
        STAMP DATE NOT NULL,
        PRIMARY KEY (CREATOR, TARGET),
        CONSTRAINT FK_CREATOR FOREIGN KEY (CREATOR) REFERENCES USERS(USER_ID),
        CONSTRAINT FK_TARGET FOREIGN KEY (TARGET) REFERENCES USERS(USER_ID)
    );

    CREATE TABLE ORDERS(
        ORDER_ID SERIAL PRIMARY KEY,
        CUSTOMER INTEGER NOT NULL,
        PRODUCT_ID INTEGER NOT NULL,
        STATUS VARCHAR(255) NOT NULL,
        STAMP DATE NOT NULL,
        CONSTRAINT FK_CUSTOMER FOREIGN KEY (CUSTOMER) REFERENCES USERS(USER_ID),
        CONSTRAINT FK_PRODUCT_ID FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID)
    );

    CREATE TABLE REPORTS(
        CREATOR INTEGER NOT NULL,
        ORDER_ID INTEGER NOT NULL,
        PROBLEM VARCHAR(255) NOT NULL,
        STAMP DATE NOT NULL,
        PRIMARY KEY (CREATOR, ORDER_ID),
        CONSTRAINT FK_CUSTOMER FOREIGN KEY (CREATOR) REFERENCES USERS(USER_ID),
        CONSTRAINT FK_ORDER_ID FOREIGN KEY (ORDER_ID) REFERENCES ORDERS(ORDER_ID)
    );
    """
    cursor = connection.cursor()
    cursor.execute(statement)
    cursor.close()


def fillDatabase(connection):
    # Fills the database with random values

    # get the cursor
    cursor = connection.cursor()

    total_users = 100
    total_products = 0  # will determined later
    total_orders = 100
    total_reports = 30

    users = []
    products = []
    orders = []
    reports = []
    ratings = []

    # # insert admin
    # adminpw = hasher.hash("admin")
    # cursor.execute("""INSERT INTO
    #                     USERS (EMAIL, PASSPHRASE, REAL_NAME, BIRTHDAY_DATE, SEX, ADDRESS, IS_BANNED, IS_ADMIN, STAMP)
    #                     VALUES (%s, %s, %s, %s, E, None, False, True, %s)""", ('admin',adminpw, datetime.datetime(2000, 10, 10), datetime.datetime.now()))

    # create users
    for user_id in range(1, total_users+1):

        # generate values
        email = get_random_string(random.randint(12, 16))
        passphrase = get_random_string(random.randint(6, 12))
        real_name = (get_random_string(random.randint(6, 12)), get_random_string(random.randint(6, 12)))
        birthday_date = datetime.datetime(random.randint(1950, 2010), random.randint(1, 12), random.randint(1, 28))
        sex = get_random_string(1, letters="MFO")  # :)
        address = get_random_string(random.randint(40, 200))
        is_banned = False
        is_admin = False
        stamp = datetime.datetime.now()

        # save them to memory
        users.append((email, passphrase, real_name, birthday_date, sex, address, is_banned, is_admin, stamp))

        # send them to database
        statement = """INSERT INTO
                        USERS (EMAIL, PASSPHRASE, REAL_NAME, BIRTHDAY_DATE, SEX, ADDRESS, IS_BANNED, IS_ADMIN, STAMP)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(statement,
                       (email, passphrase, real_name, birthday_date, sex, address, is_banned, is_admin, stamp))

        # create products
        for product_id in range(random.randint(0, 3)):

            # generate values
            total_products += 1
            creator = user_id
            status = random.choice(["Active", "Disabled"])
            title = get_random_string(random.randint(5, 15))
            description = get_random_string(random.randint(30, 200))
            category = random.choice([str(x+1) for x in range(5)])
            price = random.random() * 100
            date_interval = (datetime.datetime(2020, random.randint(1, 6), random.randint(1, 28)), datetime.datetime(2020, random.randint(7, 12), random.randint(1, 28)))
            stamp = datetime.datetime.now()

            # save them to memory
            products.append((creator, status, title, description, category, price, date_interval, stamp))

            # send them to database
            statement = """INSERT INTO
                            PRODUCTS (CREATOR, STATUS, TITLE, DESCRIPTION, CATEGORY, PRICE, DATE_INTERVAL, STAMP)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(statement,
                           (creator, status, title, description, category, price, date_interval, stamp))

    # create orders
    for order_id in range(1, total_orders+1):

        # generate values
        product_id = order_id   # array index = id in our situation
        owner_of_product = products[product_id][0]  # index 0 is the owner's user_id
        customer = random.randint(1, total_users)   # randomly select a user (some may chosen zero or multiple times)
        while customer == owner_of_product:   # but owner can not order the hers product, make sure selecting each product only once
            customer = random.randint(1, total_users)
        status = random.choice(["Shipping", "Aborted", "Taken", "Returned"])
        stamp = datetime.datetime.now()

        # save them to memory
        orders.append((customer, product_id, status, stamp))

        # send them to database
        statement = """INSERT INTO
                        ORDERS (CUSTOMER, PRODUCT_ID, STATUS, STAMP)
                        VALUES (%s, %s, %s, %s)"""
        cursor.execute(statement,
                       (customer, product_id, status, stamp))

        # create ratings
        if(random.random() < 0.5):  # 50/50 chance to get rated

            # generate values
            creator = customer
            target = owner_of_product
            score = int(random.random() * 10)
            stamp = datetime.datetime.now()

            # save them to memory
            ratings.append((creator, target, score, stamp))

            # send them to database
            statement = """INSERT INTO
                            RATINGS (CREATOR, TARGET, SCORE, STAMP)
                            VALUES (%s, %s, %s, %s)"""
            cursor.execute(statement,
                           (creator, target, score, stamp))

    # create reports
    for dummy in range(1, total_reports+1):

        # generate values
        order_id = dummy
        creator = orders[order_id][0]   # 0th index is the customer user_id
        problem = get_random_string(random.randint(50, 100))
        stamp = datetime.datetime.now()

        # save them to memory
        reports.append((creator, order_id, problem, stamp))

        # send them to database
        statement = """INSERT INTO
                            REPORTS (CREATOR, ORDER_ID, PROBLEM, STAMP)
                            VALUES (%s, %s, %s, %s)"""
        cursor.execute(statement,
                       (creator, order_id, problem, stamp))

    cursor.close()
