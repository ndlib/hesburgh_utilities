import hesutil
import subprocess

FG_DEFAULT = 39
FG_BLACK = 30
FG_RED = 31
FG_GREEN = 32
FG_YELLOW = 33
FG_BLUE = 34
FG_MAGENTA = 35
FG_CYAN = 36
FG_LIGHT_GRAY = 37
FG_DARK_GRAY = 90
FG_LIGHT_RED = 91
FG_LIGHT_GREEN = 92
FG_LIGHT_YELLOW = 93
FG_LIGHT_BLUE = 94
FG_LIGHT_MAGENTA = 95
FG_LIGHT_CYAN = 96
FG_WHITE = 97

FG_COLORS = [
  FG_DEFAULT,
  FG_BLACK,
  FG_RED,
  FG_GREEN,
  FG_YELLOW,
  FG_BLUE,
  FG_MAGENTA,
  FG_CYAN,
  FG_LIGHT_GRAY,
  FG_DARK_GRAY,
  FG_LIGHT_RED,
  FG_LIGHT_GREEN,
  FG_LIGHT_YELLOW,
  FG_LIGHT_BLUE,
  FG_LIGHT_MAGENTA,
  FG_LIGHT_CYAN,
  FG_WHITE,
]

BG_DEFAULT = 49
BG_BLACK = 40
BG_RED = 41
BG_GREEN = 42
BG_YELLOW = 43
BG_BLUE = 44
BG_MAGENTA = 45
BG_CYAN = 46
BG_LIGHT_GRAY = 47
BG_DARK_GRAY = 100
BG_LIGHT_RED = 101
BG_LIGHT_GREEN = 102
BG_LIGHT_YELLOW = 103
BG_LIGHT_BLUE = 104
BG_LIGHT_MAGENTA = 105
BG_LIGHT_CYAN = 106
BG_WHITE = 107

BG_COLORS = [
  BG_DEFAULT,
  BG_BLACK,
  BG_RED,
  BG_GREEN,
  BG_YELLOW,
  BG_BLUE,
  BG_MAGENTA,
  BG_CYAN,
  BG_LIGHT_GRAY,
  BG_DARK_GRAY,
  BG_LIGHT_RED,
  BG_LIGHT_GREEN,
  BG_LIGHT_YELLOW,
  BG_LIGHT_BLUE,
  BG_LIGHT_MAGENTA,
  BG_LIGHT_CYAN,
  BG_WHITE,
]

BOLD = 1
DIM = 2
UNDERLINE = 4

EXTRA_FORMATS = [
  BOLD,
  DIM,
  UNDERLINE,
]

ALL_FORMATS = FG_COLORS + BG_COLORS + EXTRA_FORMATS


def _prefix():
  return "\x1B["

# tput colors
_term_colors = not hesutil.onAWS
# This method wraps the requested terminal color codes around the given message
def format(text, *args):
  if not _term_colors:
    return text

  reset = _prefix() + "0m"

  fmt = _prefix()
  for arg in args:
    if arg not in ALL_FORMATS:
      return error("'%s' is not a text format code" % arg)
    fmt += ';%s' % arg
  fmt += 'm%s%s' % (text, reset)
  return fmt


def success(text):
  return format(text, FG_GREEN)


def error(text):
  return format(text, FG_RED)


def userInput(message):
  return raw_input("\n%s\n>> " % message)


def userConfirm(message):
  return isTruthy(userInput(message))


# returns false if message doesn't uniquely denote an item in the options list
# eg 'y' uniquely denotes 'yes' in the options ['yes', 'no'] but nothing in ['young', 'yellow']
def isValidInput(message, options):
  validOptions = options
  # iterate through each letter
  for index in xrange(len(message)):
    if len(validOptions) == 0:
      return False

    letter = message[index]

    tmpOptions = []
    # check this letter index in every valid option, remove those that don't match from valid options
    for option in validOptions:
      if len(option) > index and option[index] == letter:
        tmpOptions.append(option)
    validOptions = tmpOptions

  if len(validOptions) != 1:
    return False

  return validOptions[0]


def getValidInput(message, options):
  valid = False
  while not valid:
    data = userInput(message)
    valid = isValidInput(data, options)

  return valid


# run a console command - eg "yarn test"
def executeCommand(cmd):
  try:
    output = subprocess.check_output(cmd, shell=True)
    return {
      "output": output,
      "code": 0,
    }
  except subprocess.CalledProcessError as e:
    return {
      "output": e.output,
      "code": e.returncode,
    }


def isTruthy(text):
  text = text.lower()
  return isValidInput(text, ["yes"])

# this method exists so we can conditionally change where we write to in the future
#  for instance, an interactive terminal instead of just a normal stdout
def write(msg):
  # if not hesutil.onAWS:
  print msg

