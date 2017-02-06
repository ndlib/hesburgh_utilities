from datetime import datetime
import inspect

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
    def __init__(self, levels, coreContext, outFile):
      self.outFile = outFile
      self.levels = levels
      self.coreContext = coreContext


    def _log(self, message):
      print message


    def _getPrefix(self, level):
      dateStr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
      return "%s ::%s:: " % (dateStr, self.levels.get(level, "UNKNOWN"))


    def _format(self, message, **kwargs):
      coreCopy = self.coreContext.copy()
      coreCopy.update(kwargs)
      if coreCopy:
        out = ""
        for k,v in coreCopy.iteritems():
          out += "%s=%s | " % (k,v)
        out += "%s" % (message)
      else:
        out = "%s" % message
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
      self.coreContext = context


  def __new__(self, level = LEVELS, coreContext = {}, outFile = None):
    if Logger.__instance is None:
      Logger.__instance = Logger.__onlyOne(level, coreContext, outFile)
    return Logger.__instance


  def __getattr__(self, name):
    return getattr(self.__instance, name)


def _origin():
  # Get frame from 2 functions ago (should be the caller of the global log function)
  frame = inspect.stack()[2]
  # 1 = file 2 = line number
  return "%s:%s" % (frame[1], frame[2])


def setContext(context={}):
  Logger().setContext(context)


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
  kwargs["_code_origin"] = _origin()
  Logger().log(LEVEL_ERROR, message, **kwargs)


def setLevels(*levels):
  Logger().setLevels(*levels)


def setOutfile(filename):
  info("file output currently not implemented")

