from flask import Flask, render_template, request, redirect

# todo: create sessions for each ip
logged = False
app = Flask(__name__)


@app.route('/my-profile')
def my_profile_page():
    return render_template('my-profile.html', logged=True)


@app.route('/login')
def login_page():
    global logged

    # first check arguments
    login_username = request.args.get('username')
    login_password = request.args.get('password')

    # check for login attempt
    if (login_username == None or login_password == None):

        # no attempt
        # then look if machine already logged in
        if logged == True:
            return redirect('/')

        # nope not logged in...
        else:
            return render_template('login.html', logged=False)

    # there is an attempt
    else:

        # login successfull
        if(login_username == 'ali' and login_password == '123'):
            logged = True   # set logged true for ~that user~
            return redirect('/')

        # invalid login
        else:
            return "HATA!!!"  # todo: show error page


@app.route('/signup')
def signup_page():
    return render_template('signup.html', logged=logged)


@app.route('/rent-item')
def rent_item_page():
    product_id = request.args.get('productId')
    return render_template('rent-item.html', product_id=product_id, isValid=False, order_id=123123, logged=logged)


@app.route('/')
def home_page():
    return render_template('home.html',
                           logged=logged,
                           total_item=162703,
                           products=[
                               [123456, 'car', 'tih is a nice car', 233,
                                   '12.12.2020', '12.15.2020', 4/5],
                               [123456, 'car', 'tih is a nice car', 233,
                                   '12.12.2020', '12.15.2020', 4/5],
                               [123456, 'car', 'tih is a nice car', 233,
                                   '12.12.2020', '12.15.2020', 4/5],
                               [123456, 'car', 'tih is a nice car', 233,
                                   '12.12.2020', '12.15.2020', 4/5],
                               [123456, 'car', 'tih is a nice car', 233,
                                   '12.12.2020', '12.15.2020', 4/5],
                               [123456, 'car', 'tih is a nice car', 233,
                                   '12.12.2020', '12.15.2020', 4/5],
                               [123456, 'car', 'tih is a nice car', 233,
                                   '12.12.2020', '12.15.2020', 4/5]])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
