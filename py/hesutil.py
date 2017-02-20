import os
import sys
import boto3
from base64 import b64decode

# This allowes decrypted values to only be decrypted once per lambda container
decrypted = {}

onAWS = os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", False)

def getEnv(key, default=None, throw=False):
  if key not in os.environ and throw:
    raise Exception("Key \"%s\" is not in the environment" % key)

  if key in decrypted:
    return decrypted[key]

  val = os.environ.get(key, default)
  # Decrypt in KMS when we get to that point
  # if onAWS:
  #   val = boto3.client('kms').decrypt(CiphertextBlob=b64decode(val))['Plaintext']
  decrypted[key] = val

  return val


def addModulePath(base, path):
  here = os.path.dirname(os.path.relpath(base))
  sys.path.append(os.path.join(here, path))
