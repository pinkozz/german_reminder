import time

def get_time():
    hour = time.gmtime().tm_hour
    minute = time.gmtime().tm_min
    return [hour, minute]