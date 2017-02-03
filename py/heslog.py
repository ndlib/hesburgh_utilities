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
    def __init__(self, levels, outFile):
      self.outFile = outFile
      self.levels = levels


    def _origin(self):
      # Get frame from 4 functions ago (should be the caller of the global log function)
      frame = inspect.stack()[4]
      # 1 = file 2 = line number
      return "%s:%s -- " % (frame[1], frame[2])


    def _log(self, message):
      print message


    def _getPrefix(self, level):
      dateStr = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
      return "%s ::%s:: " % (dateStr, self.levels.get(level, "UNKNOWN"))


    def _format(self, message, **kwargs):
      out = "%s" % message
      if kwargs.get("withOrigin", False):
        out = "%s %s" % (self._origin(), message)

      return out


    def log(self, level, message, **kwargs):
      if level in self.levels:
        outStr = self._getPrefix(level) + self._format(message, **kwargs)
        self._log(outStr)


    def setLevels(self, *levels):
      self.levels = { k: LEVELS.get(k) for k in levels }


  def __new__(self, level = LEVELS, outFile = None):
    if Logger.__instance is None:
      Logger.__instance = Logger.__onlyOne(level, outFile)
    return Logger.__instance


  def __getattr__(self, name):
    return getattr(self.__instance, name)


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
  if "withOrigin" not in kwargs:
    kwargs["withOrigin"] = True

  Logger().log(LEVEL_ERROR, message, **kwargs)


def setLevels(*levels):
  Logger().setLevels(*levels)


def setOutfile(filename):
  info("file output currently not implemented")

