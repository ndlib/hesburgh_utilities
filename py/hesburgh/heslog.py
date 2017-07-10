from datetime import datetime
import inspect

import hesutil

LEVEL_DEBUG   = 0
LEVEL_VERBOSE = 3
LEVEL_TEST    = 5
LEVEL_INFO    = 10
LEVEL_WARN    = 40
LEVEL_ERROR   = 50

LEVELS = {
  LEVEL_DEBUG: "DEBUG",
  LEVEL_VERBOSE: "VERBOSE",
  LEVEL_TEST: "TEST",
  LEVEL_INFO: "INFO",
  LEVEL_WARN: "WARN",
  LEVEL_ERROR: "ERROR",
}

# grock
# LEVELS (DEBUG|TEST|VERBOSE|INFO||WARN|ERROR)
# %{TIMESTAMP_ISO8601:timestamp} ::%{LEVELS:level}:: %{GREEDYDATA:message}

class Logger(object):
  __instance = None

  class __onlyOne(object):
    def __init__(self, outFile):
      self.outFile = outFile

      useDebug = hesutil.getEnv("HESLOG_DEBUG", not hesutil.onAWS)
      if useDebug == True or useDebug == "true" or useDebug == "True" or useDebug == "t":
        self.levels = LEVELS
      else:
        self.levels = {
          LEVEL_INFO: LEVELS[LEVEL_INFO],
          LEVEL_WARN: LEVELS[LEVEL_WARN],
          LEVEL_ERROR: LEVELS[LEVEL_ERROR],
        }
      self.coreContext = {}


    def _log(self, message):
      print message


    def _getPrefix(self, level):
      dateStr = ""
      # AWS doesn't log the datetime in python logs else -> if not hesutil.onAWS:
      dateStr = "%s " % datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

      return u"%s::%s:: " % (dateStr, self.levels.get(level, "UNKNOWN"))


    def _format(self, message, **kwargs):
      coreCopy = self.coreContext.copy()
      coreCopy.update(kwargs)
      if coreCopy:
        out = u""
        for k,v in coreCopy.iteritems():
          out += u"%s=%s | " % (k,v)
        out += u"message=%s" % (message)
      else:
        out = u"message=%s" % message
      return out


    def log(self, level, message, **kwargs):
      if level in self.levels:
        outStr = self._getPrefix(level) + self._format(message, **kwargs)
        self._log(outStr)


    def setLevels(self, *levels):
      if not levels:
        self.levels = LEVELS
        return
      self.levels = { k: LEVELS.get(k) for k in levels }


    def setContext(self, context):
      assert context is None or type(context) is dict
      if context is None:
        context = {}
      self.coreContext = context


    def addContext(self, context):
      self.coreContext.update(context)


    def removeContext(self, keys):
      for key in keys:
        if key in self.coreContext:
          self.coreContext.pop(key, None)


  def __new__(self, outFile = None):
    if Logger.__instance is None:
      Logger.__instance = Logger.__onlyOne(outFile)

    return Logger.__instance


  def __getattr__(self, name):
    return getattr(self.__instance, name)


def _origin():
  # Get frame from 2 functions ago (should be the caller of the global log function)
  frame = inspect.stack()[2]
  # 1 = file 2 = line number
  return u"%s:%s" % (frame[1], frame[2])


def setContext(context=None):
  Logger().setContext(context)


def addContext(context=None, **kwargs):
  if context is None:
    context = {}
  context.update(kwargs)
  Logger().addContext(context)


def removeContext(*args):
  Logger().removeContext(args)


def addLambdaContext(event, context, **kwargs):
  addContext(
    api_requestId = event.get("requestContext", {}).get("requestId", ""),
    lambda_requestId = context.aws_request_id if context and context.aws_request_id else "",
    **kwargs
  )


def debug(message, **kwargs):
  Logger().log(LEVEL_DEBUG, message, **kwargs)


def verbose(message, **kwargs):
  Logger().log(LEVEL_VERBOSE, message, **kwargs)


def test(message, **kwargs):
  Logger().log(LEVEL_TEST, message, **kwargs)


def info(message, **kwargs):
  Logger().log(LEVEL_INFO,  message, **kwargs)


def warn(message, **kwargs):
  Logger().log(LEVEL_WARN, message, **kwargs)


def error(message, **kwargs):
  # kwargs["_code_origin"] = _origin()
  Logger().log(LEVEL_ERROR, message, **kwargs)


def setLevels(*levels):
  Logger().setLevels(*levels)


def setOutfile(filename):
  info("file output currently not implemented")

