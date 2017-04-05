# hesburgh_utilities

This project contains shared utilities to be used across all projects in multiple languages - currently Javascript and Python.

#### NOTE: Unless otherwise stated all utilities are avaialable in all supported languages, even if they don't have usage examples in that language.
#### NOTE: On AWS heslog defaults to only logging INFO, WARN, and ERROR levels while locally all default to being on. To override in either environment set the env var HESBURGH_DEBUG=[true|false] to the appropriate value for what you want.

## Instilation
To install projects locally run ./setup.sh in the home directory. This will install the python module and link the javascript module to your global namespace.

### JS
To install in a javascript project run `npm link hesburgh_util` in said project. This will link the globaly installed project to your local project. All `link` commands are creating symlinks so future development on the javascript project will automatically update any projects containting this one.

### PY
To install the python library to another project, you must run `ln -s "/usr/local/lib/python2.7/site-packages/hesburgh"` in that project directory. This is only needed if your project is going to be packaged for lambda, as it must exist in the directory to be zipped up. Please also add "hesburgh/" to your .gitignore file after doing this.

## Utilities:
### Logger (heslog)

#### Grock output
```
LEVELS (DEBUG|TEST|VERBOSE|INFO||WARN|ERROR)
%{TIMESTAMP_ISO8601:timestamp} ::%{LEVELS:level}:: %{GREEDYDATA:message}
```
### Example Output
A basic log prints date, time, logtype, context (key,value pairs separated by |'s) and finally the message eg:

`2017-02-08 21:06:27.328743 ::DEBUG:: lambda_requestId=some_id | request_code=github | api_requestId=some_other_id | printing this debug message`

Note: date/time will not be printed on AWS as they already add that to logs. It can easily be added back if we ever need it though.
#### Formats output for easier, uniform parsing

| Function | Parameters | Description
|----------|------------|------------
| debug    |            | Output debug log info
|          | message    | String: message to output
|          | context | Optional: Dict in JS, kwargs in PY - context information
| verbose  |            | Output verbose log info
|          | message    | String: message to output
|          | context | Optional: Dict in JS, kwargs in PY - context information
| test     |            | output test log info
|          | message    | String: message to output
|          | context | Optional: Dict in JS, kwargs in PY - context information
| info     |            | output info log info
|          | message    | String: message to output
|          | context | Optional: Dict in JS, kwargs in PY - context information
| warn     |            | Output warn info
|          | message    | String: message to output
|          | context | Optional: Dict in JS, kwargs in PY - context information
| error    |            | Output error log info
|          | message    | String: message to output
|          | context | Optional: Dict in JS, kwargs in PY - context information
| setContext |           | Set the general context that will print with every message
|          | context    | Dictionary: arbitrary key-value pairs denoting context
| addContext |           | Add values to the general context
|          | context    | (optional in py) Dictionary: arbitrary key-value pairs denoting context
|          | (py only)**kwargs | optional arbitrary key-value pairs denoting context
| removeContext |           | Remove values from the general context
|          | 1 or more strings | Variable number of keys to remove
| addLambdaContext |           | Add the basic lambda context information (request id, etc)
|          | event      | The event passed in from the lambda
|          | context    | The context passed in from the lambda
|          | (js only)extra | optional Dictionary: arbitrary key-value pairs denoting context
|          | (py only)**kwargs | optional arbitrary key-value pairs denoting context
| setLevels |            | Set what log tags will produce output
|          | 1 or more heslog levels | As defined in heslog (eg. heslog.LEVEL_ERROR)


#### Usage in Python
```
import heslog

heslog.setContext({"foo": "bar"})
heslog.debug("message")
heslog.addContext({"bar": "baz"})
heslog.error("message", foo="baz", context="here") # this overrides foo for this message only
heslog.removeContext("bar", "foo") # remove foo and bar from the context
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
const hesburgh = require("hesburgh_util");
const heslog = hesburgh.heslog;

heslog.setContext({foo: "bar"});
heslog.debug("message", {foo: "baz", context: "here"});
heslog.setLevels(heslog.levels.debug);
heslog.setLevels(heslog.levels.debug, heslog.levels.error);
...
// same format as python from here on out (which is the whole point)
```

### Utils (hesutil)
| Function | Parameters | Description
|----------|------------|------------
| getEnv   |            | Get an environment variable or default if it doesn't exist or throw if it doesn't exist
|          | key        | String: key to get
|          | defaultVal | Optional String: Default value to use if key doesn't exist
|          | shouldThrow | Optional Boolean: If true, will throw an error if key doesn't exist
| getEnvEncrypted   |            | Get an AWS-KMS encrypted environment variable or default if it doesn't exist or throw if it doesn't exist
|          | key        | String: key to get
|          | callback        | function(err, decryptedValue): Function to callback once decrypted. err will be populated if any error was encountered
|          | defaultVal | Optional String: Default value to use if key doesn't exist
|          | shouldThrow | Optional Boolean: If true, will throw an error if key doesn't exist
| dictHas(js only) |    | Check if dictionary has key
|          | dict       | Dictionary: The dictionary to use
|          | key        | String: the key to check
| dictGet(js only) |    | A safe key retrieval for JS dictionaries
|          | dict       | Dictionary: The dictionary to use
|          | key        | String: the key to get
|          | defaultVal | String: default value to return if key doesn't exist

#### JS
```
const hesburgh = require("hesburgh_util");
const hesutil = hesburgh.hesutil;

var value = hesutil.getEnv("key", "defaultValue");

//safely get value from a dictionary
var foo = hesutil.dictGet(testDict, "key", "defaultVal");

// check if a dictionary has a key
var has = hesutil.dictHas(testDict, "key")
```

### Test data (hestest)
#### NOTE: The file `datakeys.json` is expected to be in the test data (whatever you name it) folder, schema described below
| Function | Parameters | Description
|----------|------------|------------
| init     |            | Initialize the test data from specified location
|          | base       | String: The base location of the test data
|          | folder     | String: The name of the folder
| get      |            | Get the data for specified netid, if it exists
|          | netid      | String: the netid to check for
|          | default    | Optional String: A default value if the netid is not a test account (defaults to null)

#### datakeys.json
For the most part, this is just a generic json file, it will be what's returned if the netid is found in the `get` call. There is one extra option: if the value is `{ "load_file": "file.json" }` that file will be loaded and replace the value with its contents. The `file.json` value must be a relative path to the `datakeys.json` file. This allows for logical splitting of data.
```
// datakeys.json
{
  "key": "value",
  "foo": { "load_file": "bar.json" }
}
```
```
// bar.json
{
  "barkey": "barvalue",
}
```
An example of what the return will be with the above data:
```
foo = hestest.get("test_netid")
# foo = { "key": "value", "barkey", "barvalue" }
```
The `load_file` key can be used at any level, the entire tree will be traversed to load all files. So in the example `bar.json` could also contain a `load_file` to load another file.
#### Python
```
from hesburgh import hestest

# __file__ is required as the first param in python, it denotes the location of the calling file
# Then the second param is the relative path of the test data folder
hestest.init(__file__, "../testdata")
hestest.get("hbeachey")
```
#### JS
```
const hesburgh = require("hesburgh_util");
const hestest = hesburgh.hestest;

# In JS the setup is slightly different, the first param is the relative path
# The second param is the test data folder name
hestest.init("./", "testdata")
hestest.get("hbeachey")
```

### Timer (in hesutil)
| Function | Parameters | Description
|----------|------------|------------
| start    |            | start the timer
|          | start      | Optional bool (default False): start the timer immediatly
| step     |            | mark a step in time, returns dt from the start time
|          | returnDTFromPrev | Optional bool (default False): return the dt from the previous step instead of from start time, if no previous step exists, will return dt from start
| getAvgStep |          | Get the average time for each step
| getSteps |            | Get the array of steps
| end      |            | Stop the timer/Get the total time

#### Python
```
from hesburgh import hesutil

timer = hesutil.Timer()
timer.start()
# do stuff
dt = timer.step()
# do stuff
totalTime = timer.end()
avgTime = timer.getAvgStep()
```
