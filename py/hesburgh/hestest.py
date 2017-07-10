import os
import json
import heslog

_testData = {}

_basepath = "testdata"
_basefile = "accounts.json"

def _makePath(file):
  return "%s/%s" % (_basepath, file)


def _exists(file):
  return os.path.exists(_makePath(file))


_files = {}
def _recurse(data):
  for k,v in data.iteritems():
    if k == "load_file":
      return _parseJson(v).get("data", {})
    elif type(v) is dict:
      data[k] = _recurse(v)
  return data


def _parseJson(file):
  if file in _files:
    return _files[file]

  try:
    with open(_makePath(file)) as f:
      data = _recurse(json.loads(f.read()))
      _files[file] = data
      return data
  except Exception as err:
    heslog.error(err, file=file)
  return {}


def _createData(base, folder):
  global _basepath
  global _testData
  _basepath = os.path.dirname(os.path.realpath(__file__)) + "/" + _basepath

  if os.path.isdir(_basepath) and _exists(_basefile):
    _testData = _parseJson(_basefile)

    _basepath = os.path.dirname(os.path.realpath(base)) + "/" + folder
    print _basepath
    _testData["keys"] = _parseJson("datakeys.json")


def init(base, folder):
  global _testData
  if _testData:
    return
  _createData(base, folder)


def get(netid, default=None):
  if netid in _testData.get("netids", []):
    return _testData.get("keys", default)
