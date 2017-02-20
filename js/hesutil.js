// const AWS = require('aws-sdk');
const onAWS = dictHas(process.env, "AWS_LAMBDA_FUNCTION_VERSION");

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

  var val = dictGet(process.env, key, defaultVal);

  // Decrypt in KMS when we get to that point
  // if(onAWS)
  // {
  //   const kms = new AWS.KMS();
  //   kms.decrypt({ CiphertextBlob: new Buffer(val, 'base64') }, (err, data) => {
  //     if (err) {
  //       console.log('Decrypt error:', err);
  //       throw err;
  //     }
  //     val = data.Plaintext.toString('ascii');
  //   });
  // }
  decrypted[key] = val;

  return val;
}


module.exports = {
  dictHas: dictHas,
  dictGet: dictGet,
  getEnv: getEnv,
  onAWS: onAWS,
};