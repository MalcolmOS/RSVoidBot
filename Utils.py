import string
import random


def generate_user_token():
    token = ''
    for i in range(0, 20):
        token += random.choice(string.ascii_letters)
    return token
