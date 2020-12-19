from flask import Flask, render_template, request, redirect

# todo: create sessions for each ip
#todo: fix paramters for templates
logged = True
app = Flask(__name__)


@app.route('/my-profile')
def my_profile_page():
    # check for banning in admin
    return render_template('my-profile.html', logged=logged, admin=False,
                           hasProducts=True,
                           hasOrders=True,
                           orders=[
                               {'id': 123123, 'customer': 'asd@asd.com',
                                   'product_name': 'alican', 'product_id': 1231283}
                           ],
                           users=[
                               {'email': 'asd@asd.com',
                                   'name': "James jcoan", 'is_banned': False},
                               {'email': 'asd@asd.com',
                                   'name': "James jcoan", 'is_banned': False},
                               {'email': 'asd@asd.com',
                                   'name': "James jcoan", 'is_banned': True},
                               {'email': 'asd@asd.com',
                                   'name': "James jcoan", 'is_banned': False},
                               {'email': 'asd@asd.com',
                                   'name': "James jcoan", 'is_banned': False}
                           ],
                           products=[
                               {
                                   'title': 'el carrot',
                                   'description': 'this is naica',
                                   'price': 123,
                                   'dates': {
                                       'begin': '12-12-2020',
                                       'end': '21-12-2020'
                                   },
                                   'rating': '4/5'
                               },
                               {
                                   'title': 'el carrot',
                                   'description': 'this is naica',
                                   'price': 123,
                                   'dates': {
                                       'begin': '12-12-2020',
                                       'end': '21-12-2020'
                                   },
                                   'rating': '4/5'
                               },
                               {
                                   'title': 'el carrot',
                                   'description': 'this is naica',
                                   'price': 123,
                                   'dates': {
                                       'begin': '12-12-2020',
                                       'end': '21-12-2020'
                                   },
                                   'rating': '4/5'
                               }
                           ])


@app.route('/login')
def login_page():
    global logged

    # first check arguments
    login_email = request.args.get('email')
    login_password = request.args.get('password')

    # check for login attempt
    if (login_email == None or login_password == None):

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
        if(login_email == 'ali' and login_password == '123'):
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
    return render_template('rent-item.html', product_id=product_id, isValid=False, order_id=123123, logged=logged, reason='cunku sucuk')


@app.route('/')
def home_page():
    return render_template('home.html',
                           logged=logged,
                           total_item=2,
                           products=[
                               {
                                   'id': 8818,
                                   'title': 'el carrot',
                                   'description': 'this is naica',
                                   'price': 123,
                                   'dates': {
                                       'begin': '12-12-2020',
                                       'end': '21-12-2020'
                                   },
                               },
                               {
                                   'id': 8818,
                                   'title': 'el carrot',
                                   'description': 'this is naica',
                                   'price': 123,
                                   'dates': {
                                       'begin': '12-12-2020',
                                       'end': '21-12-2020'
                                   },
                               }
                           ])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
