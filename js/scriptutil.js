const hesutil = require('./hesutil')

const FG_DEFAULT = 39
const FG_BLACK = 30
const FG_RED = 31
const FG_GREEN = 32
const FG_YELLOW = 33
const FG_BLUE = 34
const FG_MAGENTA = 35
const FG_CYAN = 36
const FG_LIGHT_GRAY = 37
const FG_DARK_GRAY = 90
const FG_LIGHT_RED = 91
const FG_LIGHT_GREEN = 92
const FG_LIGHT_YELLOW = 93
const FG_LIGHT_BLUE = 94
const FG_LIGHT_MAGENTA = 95
const FG_LIGHT_CYAN = 96
const FG_WHITE = 97

const FG_COLORS = [
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

const BG_DEFAULT = 49
const BG_BLACK = 40
const BG_RED = 41
const BG_GREEN = 42
const BG_YELLOW = 43
const BG_BLUE = 44
const BG_MAGENTA = 45
const BG_CYAN = 46
const BG_LIGHT_GRAY = 47
const BG_DARK_GRAY = 100
const BG_LIGHT_RED = 101
const BG_LIGHT_GREEN = 102
const BG_LIGHT_YELLOW = 103
const BG_LIGHT_BLUE = 104
const BG_LIGHT_MAGENTA = 105
const BG_LIGHT_CYAN = 106
const BG_WHITE = 107

const BG_COLORS = [
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

const BOLD = 1
const DIM = 2
const UNDERLINE = 4

const EXTRA_FORMATS = [
  BOLD,
  DIM,
  UNDERLINE,
]

const ALL_FORMATS = FG_COLORS.concat(BG_COLORS, EXTRA_FORMATS)

function _prefix() {
  return "\x1B["
}

// tput colors
const _term_colors = !hesutil.onAWS
// This method wraps the requested terminal color codes around the given message
function format() {
  if (arguments.length === 0) {
    return null
  }

  let text = arguments[0]
  if (!_term_colors || arguments.length === 1) {
    return text
  }

  const reset = _prefix() + "0m"

  let fmt = _prefix()
  for (let index in arguments) {
    if (index === "0") {
      continue
    }
    let arg = arguments[index]
    if (!ALL_FORMATS.includes(arg)) {
      return error(arg + " is not a text format code")
    }
    fmt += `;${arg}`
  }
  fmt += `m${text}${reset}`
  return fmt
}


function success(text) {
  return format(text, FG_GREEN)
}

function error(text) {
  return format(text, FG_RED)
}

module.exports = {
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

  FG_COLORS,

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

  BG_COLORS,

  BOLD,
  DIM,
  UNDERLINE,

  EXTRA_FORMATS,
  ALL_FORMATS,

  format,
  success,
  error,
}
