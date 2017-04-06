var fs = require("fs")
var heslog = require("./heslog")
var hesutil = require("./hesutil")

var _testData = null

var _basepath = "testdata"
const _basefile = "accounts.json"


function _makePath(file) {
  return _basepath + "/" + file
}

function _recurse(data) {
  for(var k in data) {
    var v = data[k];

    if(k == "load_file") {
      return hesutil.dictGet(_parseJson(v), "data", {})
    }
    else if(typeof(v) == "object") {
      data[k] = _recurse(v)
    }
  }
  return data
}

var _files = {}
function _parseJson(file) {
  if(hesutil.dictHas(_files, file)) {
    return hesutil.dictGet(_files, file);
  }

  try {
    var str = fs.readFileSync(_makePath(file))
    var data = _recurse(JSON.parse(str))
    _files[file] = data
    return data;
  } catch(err) {
    if(err.code === 'ENOENT') {
      heslog.error(file + " does not exist")
      return {};
    }
    else {
      heslog.error(file + " error")
      console.log(err)
      return {};
    }
  }
}

function _createData(base, folder) {
  _basepath = __dirname + "/testdata"
  _testData = _parseJson(_basefile)

  _basepath = base + "/" + folder;
  _testData["keys"] = _parseJson("datakeys.json")
}

function init(base, folder) {
  if(_testData) {
    return;
  }
  _testData = {}
  _createData(base, folder)
}

function get(key, defaultVal) {
  if(defaultVal == undefined) {
    defaultVal = null
  }

  if(_testData["netids"].indexOf(key) >= 0) {
    return hesutil.dictGet(_testData, "keys")
  }
  return defaultVal
}

module.exports = {
  init: init,
  get: get,
}
