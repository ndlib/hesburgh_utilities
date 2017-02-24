const onAWS = dictHas(process.env, "AWS_LAMBDA_FUNCTION_VERSION");

var decrypt = (key, defaultVal) => {
  return dictGet(process.env, key, defaultVal);
}

// Try to import the aws-sdk, will always work on aws but may fail locally
try {
  var AWS = require('aws-sdk');
  if(onAWS) {
    decrypt = (key, defaultVal) => {
      const kms = new AWS.KMS();
      var val = dictGet(process.env, key, defaultVal);
      if(typeof val === "string") {
        kms.decrypt({ CiphertextBlob: new Buffer(val, 'base64') }, (err, data) => {
          if (err) {
            console.log(err.message);
            console.log("Couldn't decode value for key " + key + " using env val");
            return val;
          }
          return data.Plaintext.toString('ascii');
        });
      }
      return val;
    }
  }
} catch (ex) {
  // nothing
}

// This allowes decrypted values to only be decrypted once per lambda container
var decrypted = {};

function dictHas(dict, key) {
  if(dict == null) {
    return false;
  }
  return dict.hasOwnProperty(key);
}

function dictGet(dict, key, defaultVal) {
  if(dictHas(dict, key)) {
    return dict[key];
  }
  return defaultVal;
}

function getEnv(key, defaultVal, shouldThrow) {
  // handle default and throw and also get actual key
  if(!dictHas(process.env, key) && shouldThrow) {
    throw "Key \"" + key + "\" is not in the environment";
  }

  if(dictHas(decrypted, key)) {
    return dictGet(decrypted, key, defaultVal);
  }

  var val = decrypt(key, defaultVal);
  decrypted[key] = val;

  return val;
}


module.exports = {
  dictHas: dictHas,
  dictGet: dictGet,
  getEnv: getEnv,
  onAWS: onAWS,
};