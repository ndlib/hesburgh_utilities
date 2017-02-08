import os
import sys

def getEnv(key, default=None, throw=False):
  if key not in os.environ and throw:
    raise Exception("Key \"%s\" is not in the environment" % key)
  return os.environ.get(key, default)

def addModulePath(base, path):
  here = os.path.dirname(os.path.relpath(base))
  sys.path.append(os.path.join(here, path))
