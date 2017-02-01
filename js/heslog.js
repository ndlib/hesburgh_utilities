'use strict'

const HESLOG_KEY = "library.nd.edu.logger";

const LEVEL_DEBUG   = 0;
const LEVEL_VERBOSE = 3;
const LEVEL_TEST    = 5;
const LEVEL_INFO    = 10;
const LEVEL_WARN    = 40;
const LEVEL_ERROR   = 50;

var LEVELS = {};
LEVELS[LEVEL_DEBUG] = "DEBUG";
LEVELS[LEVEL_VERBOSE] = "VERBOSE";
LEVELS[LEVEL_TEST] = "TEST";
LEVELS[LEVEL_INFO] = "INFO";
LEVELS[LEVEL_WARN] = "WARN";
LEVELS[LEVEL_ERROR] = "ERROR";

// grock
// LEVELS (DEBUG|TEST|VERBOSE|INFO||WARN|ERROR)
// %{TIMESTAMP_ISO8601:timestamp} ::%{LEVELS:level}:: %{GREEDYDATA:message}

//TODO: these helpers should be exported to some other utility module
function dictHas(dict, key) {
  return dict.hasOwnProperty(key);
}

function dictGet(dict, key, defaultVal) {
  if(dictHas(dict, key)) {
    return dict[key];
  }
  return defaultVal;
}

function pad0(val, digits) {
  return ("00000000" + val).slice(-digits);
}

class HesLogger {
  constructor() {
    this.levels = LEVELS;
    this.outFile = null;
  }

  _origin() {
    // This isn't well supported in JS
  }

  // Format date to UTC iso-like format and log level prefix
  _getPrefix(level) {
    var date = new Date();
    date = pad0(date.getUTCFullYear(), 2) + "-" +
     pad0(date.getUTCMonth() + 1, 2) + "-" +
     pad0(date.getUTCDate(), 2) + " " +
     pad0(date.getUTCHours(), 2) + ":" +
     pad0(date.getUTCMinutes(), 2) + ":" +
     pad0(date.getUTCSeconds(), 2) + "." +
     pad0(date.getUTCMilliseconds(), 4);
    return date + " ::" + dictGet(LEVELS, level, "UNKNOWN") + ":: ";
  }

  _format(message, args) {
    var out = message;
    //handle any args to format output
    return out;
  }

  _log(outStr) {
    console.log(outStr);
  }

  log(level, message, args) {
    if(dictHas(this.levels, level)) {
      var outLog = this._getPrefix(level) + this._format(message, args);
      this._log(outLog);
    }
  }

  setLevels() {
    this.levels = {}
    for(var index in arguments) {
      var key = arguments[index];
      this.levels[key] = dictGet(LEVELS, key, "UNKNOWN");
    }
  }

  setOutfile(filename) {
    this.info("file output currently not implemented");
  }
}

// set up global singleton
var globalSymbols = Object.getOwnPropertySymbols(global);
var hasHeslog = (globalSymbols.indexOf(HESLOG_KEY) > -1);

if (!hasHeslog) {
  global[HESLOG_KEY] = new HesLogger();
}

// helper for exported functions to get singleton
function getGlobal() {
  return global[HESLOG_KEY];
}

module.exports = {
  debug: function(message, args) { getGlobal().log(LEVEL_DEBUG, message, args); },
  verbose: function(message, args) { getGlobal().log(LEVEL_VERBOSE, message, args); },
  test: function(message, args) { getGlobal().log(LEVEL_TEST, message, args); },
  info: function(message, args) { getGlobal().log(LEVEL_INFO, message, args); },
  warn: function(message, args) { getGlobal().log(LEVEL_WARN, message, args); },
  error: function(message, args) { getGlobal().log(LEVEL_ERROR, message, args); },
  setLevels: function() { gl = getGlobal(); gl.setLevels.apply(gl, arguments); },
  levels: {
    debug  : LEVEL_DEBUG,
    verbose: LEVEL_VERBOSE,
    test   : LEVEL_TEST,
    info   : LEVEL_INFO,
    warn   : LEVEL_WARN,
    error  : LEVEL_ERROR,
  }
};

