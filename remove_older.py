import datetime
import redis
import os
import dot_finder

def remove(array: list):
    r = redis.Redis()
    for i in array:
        if (datetime.datetime.utcnow() - i[1]) > datetime.timedelta(0, 0, 0, 0, 1, 0, 0):
            array.remove(i)
            try:
                r.delete(i[0])
                os.remove(i[0])
            except Exception:
                pass
#                print(("expired", array))
    return array
