'use strict'

const heslog = require('../heslog');
const hesutil = require('../hesutil');

heslog.setContext({foo: "bar"});
var message = "message";
heslog.debug(message, {this: "that"});
heslog.verbose(message);
heslog.test(message);
heslog.info(message);
heslog.warn(message);
heslog.error(message);

heslog.setLevels(heslog.levels.debug, heslog.levels.error);
heslog.setContext({bar: "baz"});

heslog.debug(message);
heslog.verbose(message);
heslog.test(message);
heslog.info(message);
heslog.warn(message);
heslog.error(message);

heslog.setContext();

//// print types test
heslog.setLevels();
function testFunc() { return "foo"; }
heslog.verbose("----------");
heslog.debug(null);
heslog.debug(heslog.debug);
heslog.debug(testFunc);
heslog.debug(undefined);
heslog.debug({foo: "bar"});
heslog.debug(["foo", "bar"]);

//// env vars test
heslog.test(hesutil.getEnv("PWD"));
heslog.test(hesutil.getEnv("test", "test"));
try {
  heslog.test(hesutil.getEnv("test", null, true));
} catch(e) {
  heslog.error(e);
}
