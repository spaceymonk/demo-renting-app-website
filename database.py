from ast import literal_eval as make_tuple

import settings
import psycopg2 as dbapi2
import datetime


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
