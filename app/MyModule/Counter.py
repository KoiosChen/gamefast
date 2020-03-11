from .. import redis_db
from datetime import date


def manage_key(key, date_type=None):
    return key + '_' + str(date.today()) if date_type == 'today' else key


def count(key, date_type=None, num=1):
    redis_db.incr(manage_key(key, date_type), amount=num)
