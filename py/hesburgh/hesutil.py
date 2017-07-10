import os
import sys
import boto3
from base64 import b64decode
import time

# This allowes decrypted values to only be decrypted once per lambda container
decrypted = {}
onAWS = os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", False)

class Timer(object):
  def __init__(self, start=False):
    self._start = time.time()
    self._end = self._start
    self._steps = []

    self._running = False
    if start:
      self.start()


  def start(self):
    self._running = True
    self._steps = []

    self._start = time.time()


  def step(self, returnDTFromPrev=False):
    if not self._running:
      return -1

    now = time.time()
    dt = now - self._start
    self._steps.append(dt)
    if returnDTFromPrev and len(self._steps) >= 2:
      return dt - self._steps[-2]
    return dt


  def getAvgStep(self):
    end = self._end if self._running else time.time()

    numSteps = len(self._steps) or 1
    return (end - self._start) / numSteps


  def getSteps(self):
    return self._steps


  def end(self):
    if not self._running:
      return self._end - self._start

    self._end = time.time()
    self._running = False

    dt = self._end - self._start
    self._steps.append(dt)
    return dt


def getEnv(key, default=None, throw=False):
  if key not in os.environ and throw:
    raise Exception("Key \"%s\" is not in the environment" % key)

  if key in decrypted:
    return decrypted[key]

  val = os.environ.get(key, default)
  # Try to decrypt if on AWS
  if onAWS and type(val) is str:
    try:
      val = boto3.client('kms').decrypt(CiphertextBlob=b64decode(val))['Plaintext']
    except Exception as e:
      print e
      print "Couldn't decrypt value for key %s using env val" % key

  decrypted[key] = val

  return val


def addModulePath(base, path):
  here = os.path.dirname(os.path.relpath(base))
  sys.path.append(os.path.join(here, path))
