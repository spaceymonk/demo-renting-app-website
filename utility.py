import random
import string

# Random string with the combination of lower and upper case
def get_random_string(length, letters = string.ascii_letters):
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
