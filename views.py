# THIS FILE IS FOR ROUTING WEBSITE

from flask import render_template, request, redirect
from flask_login import LoginManager, login_required
import database


def home_page():
    if (request.method == "GET"):
        # first fetch the data from the database
        products = database.fetch_AllProducts()
        # display it
        return render_template("home.html", total_item=len(products), products=products, logged=False, filtered=False)
    else:
        products = database.fetch_FilteredProducts(request.form)
        return render_template("home.html", total_item=len(products), products=products, logged=False, filtered=True)


def login_page():
    if (request.method == "GET"):
        return render_template("login.html", logged=False)
    else:
        return render_template("login.html", logged=False)

@login_required
def my_profile_page():
    return render_template("my-profile.html")