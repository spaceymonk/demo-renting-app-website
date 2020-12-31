from flask import Flask
import psycopg2 as dbapi2
import settings
import database_debug
import views


if __name__ == '__main__':
    with dbapi2.connect(settings.DSN) as connection:
        database_debug.initDatabase(connection)
        database_debug.fillDatabase(connection)

    app = Flask(__name__)
    app.add_url_rule("/", view_func=views.home_page, methods=["GET", "POST"])
    app.config["DEBUG"] = settings.DEBUG
    app.config["PORT"] = settings.PORT
    app.run(host='0.0.0.0', port=settings.PORT, debug=settings.DEBUG)
