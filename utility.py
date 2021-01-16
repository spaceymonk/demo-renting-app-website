# ---------------------------------------------------------------------------- #
#                                    IMPORTS                                   #
# ---------------------------------------------------------------------------- #
import random
import string


# ----------------------------- get_random_string ---------------------------- #
def get_random_string(length, letters=string.ascii_letters):
    # Generates a random string with the combination of lower and upper case letters
    # used when debugging
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
