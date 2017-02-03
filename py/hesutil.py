import os

def getEnv(key, default=None, throw=False):
  if key not in os.environ and throw:
    raise Exception("Key %s is not in the environment" % key)
  return os.environ.get(key, default)
