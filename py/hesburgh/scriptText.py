import hesutil

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

