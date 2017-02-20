'use strict'

const util = require('./hesutil');

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

function pad0(val, digits) {
  return ("00000000" + val).slice(-digits);
}

class HesLogger {
  constructor() {
    var useDebug = util.getEnv("HESLOG_DEBUG", !util.onAWS);
    console.log(useDebug);
    if(useDebug == "true" || useDebug == "True" || useDebug == "t" || useDebug == true) {
      this.levels = LEVELS;
    } else {
      this.levels = {}
      this.levels[LEVEL_INFO] = LEVELS[LEVEL_INFO];
      this.levels[LEVEL_WARN] = LEVELS[LEVEL_WARN];
      this.levels[LEVEL_ERROR] = LEVELS[LEVEL_ERROR];
    }
    this.outFile = null;
    this.coreContext = {};
  }

  // Format date to UTC iso-like format and log level prefix
  _getPrefix(level) {
    var date = "";
    if(!util.onAWS) {
      date = new Date();
      date = date.getUTCFullYear() + "-" +
       pad0(date.getUTCMonth() + 1, 2) + "-" +
       pad0(date.getUTCDate(), 2) + " " +
       pad0(date.getUTCHours(), 2) + ":" +
       pad0(date.getUTCMinutes(), 2) + ":" +
       pad0(date.getUTCSeconds(), 2) + "." +
       pad0(date.getUTCMilliseconds(), 4) + " ";
    }
    return date + "::" + util.dictGet(LEVELS, level, "UNKNOWN") + ":: ";
  }

  _format(message, args) {
    var context = Object.assign({}, this.coreContext, args);
    var out = ""
    for(var k in context) {
      out += this._toString(k) + "=" + this._toString(context[k]) + " | ";
    }
    return out + "message=" + message;
  }

  _log(outStr) {
    console.log(outStr);
  }

  _toString(obj) {
    if(typeof obj === "string") {
      return obj;
    }
    else if(typeof obj === "function") {;
      if(obj.name) {
        return "[Function: " + obj.name + "]";
      }
      return "[Function]";
    }
    else if(typeof obj === "undefined") {
      return "undefined";
    }
    else if(obj === null) {
      return "null";
    }
    else {
      return JSON.stringify(obj);
    }
  }

  log(level, message, args) {
    var output = this._toString(message);

    if(util.dictHas(this.levels, level)) {
      var outLog = this._getPrefix(level) + this._format(output, args);
      this._log(outLog);
    }
  }

  setLevels() {
    if(arguments.length == 0) {
      this.levels = LEVELS;
      return;
    }
    this.levels = {}
    for(var index in arguments) {
      var key = arguments[index];
      this.levels[key] = util.dictGet(LEVELS, key, "UNKNOWN");
    }
  }

  setContext(context) {
    this.coreContext = context;
  }

  addContext(context) {
    this.coreContext = Object.assign({}, this.coreContext, context);
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

function addLambdaContext(event, context, extra) {
  var lambdaContext = {
    api_requestId: util.dictGet(util.dictGet(event, "requestContext", {}), "requestId", ""),
    lambda_requestId: context ? context.awsRequestId : "",
  }
  getGlobal().addContext(Object.assign({}, lambdaContext, extra));
}

module.exports = {
  debug: function(message, args) { getGlobal().log(LEVEL_DEBUG, message, args); },
  verbose: function(message, args) { getGlobal().log(LEVEL_VERBOSE, message, args); },
  test: function(message, args) { getGlobal().log(LEVEL_TEST, message, args); },
  info: function(message, args) { getGlobal().log(LEVEL_INFO, message, args); },
  warn: function(message, args) { getGlobal().log(LEVEL_WARN, message, args); },
  error: function(message, args) { getGlobal().log(LEVEL_ERROR, message, args); },
  setLevels: function() { var gl = getGlobal(); gl.setLevels.apply(gl, arguments); },
  setContext: function(context) { getGlobal().setContext(context); },
  addContext: function(context) { getGlobal().addContext(context); },
  addLambdaContext: addLambdaContext,
  levels: {
    debug  : LEVEL_DEBUG,
    verbose: LEVEL_VERBOSE,
    test   : LEVEL_TEST,
    info   : LEVEL_INFO,
    warn   : LEVEL_WARN,
    error  : LEVEL_ERROR,
  }
};

