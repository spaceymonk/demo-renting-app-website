# THIS FILE IS FOR ROUTING WEBSITE

from flask import render_template, request, redirect, flash
from flask_login import login_required, login_user, logout_user, current_user
import database
import datetime


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
        user = database.validate_user(request.form.get('email'), request.form.get('password'))
        if user is not None:
            if not user.is_active():
                flash("You have been banned!!!")
                return redirect("/login")
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
        try:
            user = {
                'email': request.form.get('email'),
                'passphrase': request.form.get('passphrase'),
                'real_name': {
                    'first_name': request.form.get('first_name'),
                    'last_name': request.form.get('last_name')
                },
                'birthday_date': datetime.datetime.strptime(request.form.get('birthday_date'), "%Y-%m-%d"),
                'sex': request.form.get('sex'),
                'address': request.form.get('address'),
                'is_banned': False,
                'is_admin': False,
                'stamp': datetime.datetime.now()
            }
            database.create_user(user)
            flash("WELCOME :ddd")
            return redirect("/login")
        except:
            flash("Something went wrong!")
            return redirect('/signup')


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
    if current_user.is_admin():
        email = request.form.get('email')
        user = database.fetch_User(email)
        print(user)
        if user['is_banned']:
            try:
                database.remove_ban(email)
                flash(f"Ban removed for: {email}")
            except:
                flash("Something went wrong!")
        else:
            try:
                database.add_ban(email)
                flash(f"User banned: {email}")
            except:
                flash("Something went wrong!")
    return redirect('/my-profile')


@login_required
def delete_account_page():
    database.remove_user(current_user.get_id())
    return redirect('/logout')
