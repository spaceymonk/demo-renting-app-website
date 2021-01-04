# THIS FILE IS FOR ROUTING WEBSITE

from flask import render_template, request, redirect, flash
from flask_login import login_required, login_user
import database

def home_page():
    if (request.method == "GET"):
        # first fetch the data from the database
        products = database.fetch_AllProducts()
        # display it
        return render_template("home.html", total_item=len(products), products=products, filtered=False)
    else:
        products = database.fetch_FilteredProducts(request.form)
        return render_template("home.html", total_item=len(products), products=products, filtered=True)


def login_page():
    if (request.method == "GET"):
        return render_template("login.html")
    else:
        user = database.fetch_user(request.form.get('email'), request.form.get('password'))
        if user is not None:
            login_user(user)
            flash("You are logged in!")
            return redirect("/")
        else:
            flash("Email or password is not correct!")
            return render_template("login.html")


@login_required
def my_profile_page():
    return render_template("my-profile.html")
