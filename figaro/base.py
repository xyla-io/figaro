import time

from ratelimit import limits, sleep_and_retry
from facebook_business.exceptions import FacebookRequestError

def rate_limit(func):

  @sleep_and_retry
  @limits(calls=100, period=10)
  def wrapper(*args, **kargs):
    try:
      return func(*args, **kargs)
    except FacebookRequestError as exception:
      print(exception)
      time.sleep(90)
      return func(*args, **kargs)

  return wrapper