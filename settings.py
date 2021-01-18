# ---------------------------------------------------------------------------- #
#                                   CONSTANTS                                  #
# ---------------------------------------------------------------------------- #

# ----------------------------------- Flask ---------------------------------- #
DEBUG = False
HOST = "0.0.0.0"
PORT = os.getenv("PORT")
SECRET_KEY = "secret"

# --------------------------------- Database --------------------------------- #
import os
DSN = os.getenv("DATABASE_URL")

# -------------------------------- Application ------------------------------- #
CATEGORIES = [str(x+1) for x in range(5)]   # "name" of the categories
USERMAP = {}    # stores the user informations, used in login procudure
