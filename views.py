# THIS FILE IS FOR ROUTING WEBSITE

from flask import render_template, request, redirect, flash
from flask_login import login_required, login_user, logout_user, current_user
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
    if current_user.is_admin():
        users = database.fetch_AllUsers()
        return render_template("admin.html", users=users, length=len(users))
    else:
        return render_template("my-profile.html")


@login_required
def logout_page():
    logout_user()
    flash("Successfuly logged out!")
    return redirect('/')


def signup_page():
    if (request.method == "GET"):
        return render_template("signup.html")
    else:
        pass


@login_required
def settings_page():
    pass


@login_required
def add_product_page():
    pass


@login_required
def remove_product_page():
    pass


@login_required
def toggle_ban_page():
    pass
