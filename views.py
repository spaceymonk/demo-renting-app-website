# THIS FILE IS FOR ROUTING WEBSITE

from flask import render_template, request, redirect, flash
from flask_login import login_required, login_user, logout_user, current_user
import database
import datetime
from passlib.hash import pbkdf2_sha256 as hasher


def home_page():
    if (request.method == "GET"):
        # first fetch the data from the database
        products = database.fetch_Products_All()
        for product in products:
            product['merchant_rating'] = database.get_UserScore_ById(product['creator'])
        # display it
        return render_template("home.html", total_item=len(products), products=products, filtered=False)
    else:
        products = database.fetch_Products_ByForm(request.form)
        return render_template("home.html", total_item=len(products), products=products, filtered=True)


def login_page():
    if (request.method == "GET"):
        return render_template("login.html")
    else:
        try:
            user = database.validate_user(request.form.get('email'), request.form.get('passphrase'))
            if user is not None:
                if not user.is_active():
                    flash("You have been banned!!!", 'is-warning')
                    return redirect("/login")
                login_user(user)
                flash("You are logged in!", 'is-success')
                return redirect("/")
            else:
                flash("Email or password is not correct!", 'is-warning')
                return render_template("login.html")
        except Exception as e:
            flash(f"Something went wrong: {e}", 'is-danger')
            return render_template("login.html")


@login_required
def my_profile_page():
    try:
        if current_user.is_admin():
            users = database.fetch_Users_All()
            return render_template("admin.html", users=users, length=len(users))
        else:
            userdata = database.fetch_User_ById(current_user.id)
            products = database.fetch_Products_OfUser_ById(current_user.id)
            orders = database.fetch_Orders_OfUser_ById(current_user.id)
            # also we need to fetch order metadata as well
            for order in orders:
                order['metadata'] = database.fetch_OrderMetadata_ById(order['order_id'])
            return render_template("my-profile.html", userdata=userdata, products=products, orders=orders)
    except Exception as e:
        flash(f"Something went wrong: {e}", 'is-danger')
        return redirect('/')


@login_required
def logout_page():
    try:
        logout_user()
        flash("Successfuly logged out!", 'is-success')
        return redirect('/')
    except Exception as e:
        flash(f"Something went wrong: {e}", 'is-danger')
        return redirect('/')


def signup_page():
    if (request.method == "GET"):
        return render_template("signup.html")
    else:
        try:
            fields = {
                'email': request.form.get('email'),
                'passphrase': hasher.hash(request.form.get('passphrase')),
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
            database.create_User(fields)
            flash("Welcome!", 'is-success')
            return redirect("/login")
        except Exception as e:
            flash(f"Something went wrong: {e}", 'is-danger')
            return redirect('/signup')


@login_required
def settings_page():
    try:
        fields = {
            'passphrase': hasher.hash(request.form.get('passphrase')),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'sex': request.form.get('sex'),
            'address': request.form.get('address'),
        }
        database.update_User_ByEmail(current_user.email, fields)
        flash("Changes Saved!", 'is-success')
    except Exception as e:
        flash(f"Something went wrong: {e}", 'is-danger')
    finally:
        return redirect('/my-profile')


@login_required
def add_product_page():
    try:
        fields = {
            'creator': current_user.id,
            'status': "Active",
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'category': request.form.get('category'),
            'price': request.form.get('price'),
            'date_interval': {
                'begin_date': datetime.datetime.strptime(request.form.get('begin_date'), "%Y-%m-%d"),
                'end_date': datetime.datetime.strptime(request.form.get('end_date'), "%Y-%m-%d"),
            },
            'stamp': datetime.datetime.now(),
        }
        database.create_Product(fields)
        flash("Product Added!", 'is-success')
    except Exception as e:
        flash(f"Something went wrong: {e}", 'is-danger')
    finally:
        return redirect('/my-profile')


@login_required
def remove_product_page():
    try:
        database.delete_Product_ById(request.form.get('product_id'))
        flash('Product removed!', 'is-success')
    except Exception as e:
        flash(f"Something went wrong: {e}", 'is-danger')
    finally:
        return redirect('/my-profile')


@login_required
def toggle_ban_page():
    if current_user.is_admin():
        email = request.form.get('email')
        user = database.fetch_User_ByEmail(email)
        if user['is_banned']:
            try:
                database.update_UserBan_ByEmail(email, False)
                flash(f"Ban removed for: {email}", 'is-info')
            except:
                flash("Something went wrong!")
        else:
            try:
                database.update_UserBan_ByEmail(email, True)
                flash(f"User banned: {email}", 'is-info')
            except Exception as e:
                flash(f"Something went wrong: {e}", 'is-danger')
    return redirect('/my-profile')


@login_required
def delete_account_page():
    try:
        database.delete_User_ByEmail(current_user.email)
        flash("Account successfully deleted!", 'is-success')
        return redirect('/logout')
    except Exception as e:
        flash(f"Something went wrong: {e}", 'is-danger')
        return redirect('/my-profile')


@login_required
def rent_item_page():
    product_id = request.args.get('productId')
    if product_id is None:
        flash('Invalid product !', 'is-warning')
        return redirect('/')
    else:
        try:
            order_id, email = database.create_Order_ById(current_user.id, product_id)
            return render_template("rent-item.html", product_id=product_id, email=email, order_id=order_id)
        except Exception as e:
            flash(f"Something went wrong: {e}", 'is-danger')
            return redirect("/")


@login_required
def report_page():
    print(request.form)
    return redirect('/my-profile')


@login_required
def rate_page():
    pass


@login_required
def close_order_page():
    try:
        database.update_OrderStatus_ById(request.form.get('order_id'), 'Close')
        order = database.fetch_Order_ById(request.form.get('order_id'))
        database.update_ProductStatus_ById(order['product_id'], 'Hidden')
        flash('Order Closed!', 'is-success')
    except Exception as e:
        flash(f"Something went wrong: {e}", 'is-danger')
    finally:
        return redirect('/my-profile')
