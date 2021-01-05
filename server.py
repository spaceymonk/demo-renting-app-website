from flask import Flask
from flask_login import LoginManager
import psycopg2 as dbapi2
import settings
import database_debug
import views
import database

app = Flask(__name__)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(email):
    return settings.USERMAP.get(email)


if __name__ == '__main__':
    # with dbapi2.connect(settings.DSN) as connection:
    #     database_debug.initDatabase(connection)
    #     database_debug.fillDatabase(connection)

    login_manager.init_app(app)
    login_manager.login_view = "login_page"
    app.secret_key = settings.SECRET_KEY
    app.add_url_rule("/", view_func=views.home_page, methods=["GET", "POST"])
    app.add_url_rule("/delete-account", view_func=views.delete_account_page, methods=["GET"])
    app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
    app.add_url_rule("/signup", view_func=views.signup_page, methods=["GET", "POST"])
    app.add_url_rule("/logout", view_func=views.logout_page, methods=["GET"])
    app.add_url_rule("/my-profile", view_func=views.my_profile_page, methods=["GET", "POST"])
    app.add_url_rule("/settings", view_func=views.settings_page, methods=["POST"])
    app.add_url_rule("/add-product", view_func=views.add_product_page, methods=["POST"])
    app.add_url_rule("/remove-product", view_func=views.remove_product_page, methods=["POST"])
    app.add_url_rule("/toggle-ban", view_func=views.toggle_ban_page, methods=["POST"])
    app.run(host='0.0.0.0', port=settings.PORT, debug=settings.DEBUG)
