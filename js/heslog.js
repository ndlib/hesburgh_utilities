'use strict'

const util = require('./hesutil');
const scriptutil = require('./scriptutil');
const raven = require('raven');

const HESLOG_KEY  = "library.nd.edu.logger";

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
LEVELS[LEVEL_WARN] = scriptutil.format("WARN", scriptutil.FG_LIGHT_YELLOW);
LEVELS[LEVEL_ERROR] = scriptutil.format("ERROR", scriptutil.FG_RED);

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

  log(level, message, args, sentry) {
    var output = this._toString(message);

    if(util.dictHas(this.levels, level)) {
      var outLog = this._getPrefix(level) + this._format(output, args);
      this._log(outLog);
    }
    if((level >= LEVEL_WARN) || sentry) {
      let level_type = LEVELS[level].toLowerCase();
      if(level === LEVEL_WARN) {
        level_type = "warning"
      } else if(level === LEVEL_ERROR) {
        level_type = "error"
      }
      if(message instanceof Error) {
        raven.captureException(message.message, {extra: this.coreContext,level: level_type});
      } else {
        raven.captureMessage(message, {extra: this.coreContext,level: level_type});
      }
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

  removeContext(keys) {
    for(var index in keys) {
      var key = keys[index];
      if(util.dictHas(this.coreContext, key)) {
        delete this.coreContext[key];
      }
    }
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

const setHubContext = async (...args) => {
  const AWS = require('aws-sdk');
  const ssm = new AWS.SSM({region: "us-east-1"});
  let param = {
    Name: '/all/sentry/production/' + args[0] + '/dsn',
    WithDecryption: true
  };
  try {
    const data = await ssm.getParameter(param).promise();
    raven.config(data.Parameter.Value).install();
  } catch (err) {
    console.log(err);
    return err;
  }
}

module.exports = {
  debug: function(message, args, sentry) { getGlobal().log(LEVEL_DEBUG, message, args, sentry); },
  verbose: function(message, args, sentry) { getGlobal().log(LEVEL_VERBOSE, message, args, sentry); },
  test: function(message, args, sentry) { getGlobal().log(LEVEL_TEST, message, args, sentry); },
  info: function(message, args, sentry) { getGlobal().log(LEVEL_INFO, message, args, sentry); },
  warn: function(message, args, sentry) { getGlobal().log(LEVEL_WARN, message, args, sentry); },
  error: function(message, args, sentry) { getGlobal().log(LEVEL_ERROR, message, args, sentry); },
  setLevels: function() { var gl = getGlobal(); gl.setLevels.apply(gl, arguments); },
  setContext: function(context) { getGlobal().setContext(context); },
  addContext: function(context) { getGlobal().addContext(context); },
  removeContext: function() { getGlobal().removeContext(arguments); },
  setHubContext: setHubContext,
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

