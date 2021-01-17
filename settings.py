# ---------------------------------------------------------------------------- #
#                                   CONSTANTS                                  #
# ---------------------------------------------------------------------------- #

# ----------------------------------- Flask ---------------------------------- #
DEBUG = False
PORT = 8080
SECRET_KEY = "secret"

# --------------------------------- Database --------------------------------- #
DSN = """user=postgres password=123 dbname=renting_app_db"""

# -------------------------------- Application ------------------------------- #
CATEGORIES = [str(x+1) for x in range(5)]   # "name" of the categories
USERMAP = {}    # stores the user informations, used in login procudure
