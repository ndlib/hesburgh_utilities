function dictHas(dict, key) {
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
  var val = dictGet(process.env, key, defaultVal);
  return val;
}

module.exports = {
  dictHas: dictHas,
  dictGet: dictGet,
  getEnv: getEnv,
};