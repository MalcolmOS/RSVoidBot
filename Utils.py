import string
import random
import time
from datetime import datetime


def get_time_stamp():
    return f'[{time.ctime(datetime.timestamp(datetime.now()))}]'


def log(content):
    print(f'{get_time_stamp()} {content}')


def generate_user_token():
    token = ''
    for i in range(0, 20):
        token += random.choice(string.ascii_letters)
    return token
