# ---------------------------------------------------------------------------- #
#                                    IMPORT                                    #
# ---------------------------------------------------------------------------- #
from flask import current_app

# ---------------------------------------------------------------------------- #
#                                  USER CLASS                                  #
# ---------------------------------------------------------------------------- #
# ---------------------------- Used in Flask-Login --------------------------- #


class User():

    def __init__(self, email, authenticated, banned, admin, id):
        self.email = email
        self.authenticated = authenticated
        self.banned = banned
        self.admin = admin
        self.id = id

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return not self.banned

    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.admin
