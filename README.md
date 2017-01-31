# hesburgh_utilities

This project contains shared utilities to be used across all projects in multiple languages - currently Javascript and Python.

## Instilation
To install projects locally run ./setup.sh in the home directory. This will install the python module and link the javascript module to your global namespace.

After the above is done, to install in a javascript project run
`npm link hesburgh_util`
in said project. This will link the globaly installed project to your local project. All `link` commands are creating symlinks so future development on the javascript project will automatically update any projects containting this one.

## Grock output
```
LEVELS (DEBUG|TEST|VERBOSE|INFO||WARN|ERROR)
%{TIMESTAMP_ISO8601:timestamp} ::%{LEVELS:level}:: %{GREEDYDATA:message}
```

## Utilities:
### Logger (heslog)
#### Formats output for easier, uniform parsing

Function | Parameters | Description
---------|------------|------------
debug    | message string, [arguments] | Output debug log info
verbose  | message string, [arguments] | Output verbose log info
test     | message string, [arguments] | Output test log info
info     | message string, [arguments] | Output info log info
warn     | message string, [arguments] | Output warn log info
error    | message string, [arguments] | Output error log info
setLevels| 1 or more heslog levels | Restrict what log tags will produce output
setOutfile| output file name | !!Currently not implemented!!
* [arguments] is an optional dictionary of arguments - currently ignored


#### Usage in Python
```
import heslog

heslog.debug("message")
heslog.error("message")
...
heslog.setLevels(heslog.LEVEL_ERROR)
heslog.debug("message") # will not output to log
heslog.error("message") # only this function will output to log
...
heslog.setLevels(heslog.LEVEL_WARN, heslog.LEVEL_INFO)
# now only warn and info will output
```
#### Usage in JS
```
const hesutil = require("hesburgh_util");
const heslog = hesutil.heslog;

heslog.debug("message");
heslog.setLevels(heslog.levels.debug);
heslog.setLevels(heslog.levels.debug, heslog.levels.error);
...
// same format as python from here on out (which is the whole point)
```
