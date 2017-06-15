'use strict'
const async = require('async')

const onAWS = dictHas(process.env, "AWS_LAMBDA_FUNCTION_VERSION");

class Timer {
  constructor(start) {
    this._start = Date.now();
    this._end = this._start;
    this._steps = [];

    this._running = false;
    if(start){
      this.start();
    }
  }

  start() {
    this._running = true;
    this._steps = [];

    this._start = Date.now();
  }

  step(returnDTFromPrev) {
    if(!this._running) {
      return -1;
    }

    var now = Date.now();
    var dt = now - this._start;
    this._steps.push(dt);

    var stepsLen = this._steps.length
    if(returnDTFromPrev && stepsLen >= 2) {
      return dt - this._steps[stepsLen - 2];
    }
    return dt;
  }

  getAvgStep() {
    var end = this._end;
    if(this._running) {
      end = Date.now();
    }

    var numSteps = this._steps.length > 0 ? this._steps.length : 1;
    return (end - this._start) / numSteps;
  }

  getSteps() {
    return this._steps;
  }

  end() {
    if(!this._running) {
      return this._end - this._start;
    }

    this._end = Date.now();
    this._running = false;

    var dt = this._end - this._start;
    this._steps.push(dt);
    return dt;
  }
}

// When not on AWS, only returns the raw value
var decrypt = (key, callback, defaultVal) => {
  callback(null, dictGet(process.env, key, defaultVal));
}

// Try to import the aws-sdk, will always work on aws but may fail locally
try {
  var AWS = require('aws-sdk');
  if(onAWS) {
    decrypt = (key, callback, defaultVal) => {
      const kms = new AWS.KMS();
      var val = dictGet(process.env, key, defaultVal);
      if(typeof val === "string") {
        kms.decrypt({ CiphertextBlob: new Buffer(val, 'base64') }, (err, data) => {
          if (err) {
            return callback(err);
          }
          return callback(null, data.Plaintext.toString('ascii'));
        });
      }
      return val;
    }
  }
} catch (ex) {
  console.log("::: Couldn't import aws");
}

// This allowes decrypted values to only be decrypted once per lambda container
var decrypted = {};

function isDict(obj) {
  return typeof obj === "object"
      && obj !== null
      && obj !== undefined
      && !Array.isArray(obj)
}

function dictHas(dict, key) {
  if(!isDict(dict)) {
    return false;
  }
  return dict.hasOwnProperty(key);
}

function dictGet(dict, key, defaultVal) {
  var ret = defaultVal
  if(dictHas(dict, key)) {
    ret = dict[key];
  }

  if(isDict(ret)) {
    if(ret.hasOwnProperty("safeGet")) {
      console.log("WARNING: overwriting property 'safeGet' on dict")
    }
    ret["safeGet"] = dictGet.bind(null, ret)
  }
  return ret;
}

function getEnvsEncrypted(keys, callback, defaultVal, shouldThrow) {
  let results = []
  async.each(keys,
    function (item, next) {
      getEnvEncrypted(item, function (decryptErr, decryptedVal) {
        if (decryptErr) {
          return next(new Error(decryptErr))
        }
        results[item] = decryptedVal
        return next(null)
      })
    },
    function (err) {
      if (err) {
        return callback(new Error(err))
      }
      // All decrypted successfully
      callback(null, results)
    }
  )
}

function getEnvEncrypted(key, callback, defaultVal, shouldThrow) {
  // handle default and throw and also get actual key
  if(!dictHas(process.env, key) && shouldThrow) {
    throw "Key \"" + key + "\" is not in the environment";
  }

  if(dictHas(decrypted, key)) {
    return callback(null, dictGet(decrypted, key, defaultVal));
  }

  decrypt(key, function(err, val) {
    if(err){
      return callback(err);
    }
    decrypted[key] = val;
    return callback(null, val);
  }, defaultVal);
}

function getEnv(key, defaultVal, shouldThrow) {
  // handle default and throw and also get actual key
  if(!dictHas(process.env, key) && shouldThrow) {
    throw "Key \"" + key + "\" is not in the environment";
  }
  return dictGet(process.env, key, defaultVal);
}


module.exports = {
  dictHas: dictHas,
  dictGet: dictGet,
  getEnv: getEnv,
  getEnvEncrypted: getEnvEncrypted,
  getEnvsEncrypted: getEnvsEncrypted,
  onAWS: onAWS,
  Timer: Timer,
};
