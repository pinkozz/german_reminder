import time

def get_time():
    # UTC+03:00
    hour = time.gmtime().tm_hour+3
    minute = time.gmtime().tm_min
    return [hour, minute]