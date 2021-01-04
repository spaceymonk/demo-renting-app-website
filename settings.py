DEBUG = True
PORT = 8080

DSN = """user=postgres password=123 dbname=renting_app_db"""

CATEGORIES = [str(x+1) for x in range(5)]

SECRET_KEY = "secret"

USERMAP = {}