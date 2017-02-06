from hesburgh import heslog,hesutil

message = "message"
heslog.setContext({"foo": "bar"})

heslog.debug(message)
heslog.verbose(message)
heslog.info(message)
heslog.warn(message)
heslog.error(message)

heslog.setContext({"bar": "baz"})
heslog.setLevels(heslog.LEVEL_DEBUG, heslog.LEVEL_ERROR)

heslog.debug(message)
heslog.verbose(message) # should not print
heslog.info(message) # should not print
heslog.warn(message) # should not print
heslog.error(message)

heslog.setContext()

### print types test
heslog.setLevels()
def testFunc():
  return "foo";
heslog.verbose("----------");
heslog.debug(None);
heslog.debug(heslog.debug);
heslog.debug(testFunc);
heslog.debug({"foo": "bar"});
heslog.debug(["foo", "bar"]);

### env vars test
heslog.test(hesutil.getEnv("PWD"))
heslog.test(hesutil.getEnv("test", "default"))
try:
  heslog.test(hesutil.getEnv("test", throw=True))
except Exception as e:
  heslog.error(e)

