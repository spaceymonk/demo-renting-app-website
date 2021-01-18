# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #
from flask import Flask
from flask_login import LoginManager
import psycopg2 as dbapi2
import settings
import database_debug
import views
import database


# ---------------------------------------------------------------------------- #
#                                     INIT                                     #
# ---------------------------------------------------------------------------- #
app = Flask(__name__)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(email):
    return settings.USERMAP.get(email)


@app.errorhandler(Exception)
def global_error_handler(e):
    return f"Something terribly gone wrong! Here is some info: {e}"


# ---------------------------------------------------------------------------- #
#                                  ENTRY POINT                                 #
# ---------------------------------------------------------------------------- #
with dbapi2.connect(settings.DSN, sslmode='require') as connection:
    database_debug.initDatabase(connection)
#   database_debug.fillDatabase(connection) # for faster debugging fill database with garbage

login_manager.init_app(app)  # initialize login manager
login_manager.login_view = "login_page"  # set login page
login_manager.login_message_category = "is-info"    # set login message category
app.secret_key = settings.SECRET_KEY    # set "secret" key

# Set url entries
app.add_url_rule("/", view_func=views.home_page, methods=["GET", "POST"])
app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
app.add_url_rule("/my-profile", view_func=views.my_profile_page, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=views.logout_page, methods=["GET"])
app.add_url_rule("/signup", view_func=views.signup_page, methods=["GET", "POST"])
app.add_url_rule("/settings", view_func=views.settings_page, methods=["POST"])
app.add_url_rule("/add-product", view_func=views.add_product_page, methods=["POST"])
app.add_url_rule("/remove-product", view_func=views.remove_product_page, methods=["POST"])
app.add_url_rule("/toggle-ban", view_func=views.toggle_ban_page, methods=["POST"])
app.add_url_rule("/delete-account", view_func=views.delete_account_page, methods=["GET"])
app.add_url_rule("/rent-item", view_func=views.rent_item_page, methods=["GET"])
app.add_url_rule("/report", view_func=views.report_page, methods=["POST"])
app.add_url_rule("/rate", view_func=views.rate_page, methods=["POST"])
app.add_url_rule("/close-order", view_func=views.close_order_page, methods=["POST"])

if __name__ == "__main__":
    # run application
    app.run(host=settings.HOST, port=settings.PORT)
