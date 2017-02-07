# hesburgh_utilities

This project contains shared utilities to be used across all projects in multiple languages - currently Javascript and Python.

## Instilation
To install projects locally run ./setup.sh in the home directory. This will install the python module and link the javascript module to your global namespace.

After the above is done, to install in a javascript project run
`npm link hesburgh_util`
in said project. This will link the globaly installed project to your local project. All `link` commands are creating symlinks so future development on the javascript project will automatically update any projects containting this one.

## Utilities:
### Logger (heslog)

#### Grock output
```
LEVELS (DEBUG|TEST|VERBOSE|INFO||WARN|ERROR)
%{TIMESTAMP_ISO8601:timestamp} ::%{LEVELS:level}:: %{GREEDYDATA:message}
```
#### Formats output for easier, uniform parsing

Function | Parameters | Description
---------|------------|------------
debug    |            | Output debug log info
         | message    | String: message to output
         | context | Optional: Dict in JS, kwargs in PY - context information
verbose  |            | Output verbose log info
         | message    | String: message to output
         | context | Optional: Dict in JS, kwargs in PY - context information
test     |            | output test log info
         | message    | String: message to output
         | context | Optional: Dict in JS, kwargs in PY - context information
info     |            | output info log info
         | message    | String: message to output
         | context | Optional: Dict in JS, kwargs in PY - context information
warn     |            | Output warn info
         | message    | String: message to output
         | context | Optional: Dict in JS, kwargs in PY - context information
error    |            | Output error log info
         | message    | String: message to output
         | context | Optional: Dict in JS, kwargs in PY - context information
setContext|           | Set the general context that will print with every message
         | context    | Dictionary: arbitrary key-value pairs denoting context
setLevels|            | Set what log tags will produce output
         | 1 or more heslog levels | As defined in heslog (eg. heslog.LEVEL_ERROR)


#### Usage in Python
```
import heslog

heslog.setContext({"foo": "bar"})
heslog.debug("message")
heslog.error("message", foo="baz", context="here") # this overrides foo for this message only
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

heslog.setContext({foo: "bar"});
heslog.debug("message", {foo: "baz", context: "here"});
heslog.setLevels(heslog.levels.debug);
heslog.setLevels(heslog.levels.debug, heslog.levels.error);
...
// same format as python from here on out (which is the whole point)
```

### Utils (hesutil)
Function | Parameters | Description
---------|------------|------------
getEnv   |            | Get an environment variable or default if it doesn't exist or throw if it doesn't exist
         | key        | String: key to get
         | defaultVal | Optional String: Default value to use if key doesn't exist
         | shouldThrow | Optional Boolean: If true, will throw an error if key doesn't exist
dictHas(js only) |    | Check if dictionary has key
         | dict       | Dictionary: The dictionary to use
         | key        | String: the key to check
dictGet(js only) |    | A safe key retrieval for JS dictionaries
         | dict       | Dictionary: The dictionary to use
         | key        | String: the key to get
         | defaultVal | String: default value to return if key doesn't exist
