from flask import Flask, render_template, request, redirect
import psycopg2 as dbapi2

from initDb import *

DSN = """user=postgres password=123 dbname=renting_app_db"""

with dbapi2.connect(DSN) as connection:
    initDatabase(connection)
    fillDatabase(connection)

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
