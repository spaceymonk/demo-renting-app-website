from flask import current_app


class User():

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True


def get_user(email, password):
    user = User(email, password)
    return user
