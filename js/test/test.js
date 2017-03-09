'use strict'

const heslog = require('../heslog');
const hesutil = require('../hesutil');

heslog.setContext({foo: "bar"});
var message = "message";
heslog.debug(message, {this: "that"});
heslog.addContext({baz: "foo"});
heslog.addContext({test: "this"});
heslog.verbose(message);
heslog.test(message);
heslog.info(message);
heslog.warn(message);
heslog.error(message);

heslog.info("setting levels to debug and error");
heslog.setLevels(heslog.levels.debug, heslog.levels.error);
heslog.setContext({bar: "baz"});

heslog.debug(message);
heslog.verbose(message);
heslog.test(message);
heslog.info(message);
heslog.warn(message);
heslog.error(message);

heslog.setContext();
//
var event = {requestContext: {requestId: "api_id"}};
var context = {awsRequestId: "lambda_id"};
heslog.addLambdaContext(event, context, {extra: "test"});
heslog.debug("lambda test");

heslog.setContext();
//// print types test
heslog.debug("setting all levels");
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
// Assumes you have AWS_REGION set
hesutil.getEnvEncrypted("ENCRYPTED_PWD", heslog.test);

var timer = new hesutil.Timer()
timer.start()
heslog.test(timer.step())
heslog.test(timer.step(true))
var end = timer.end()
heslog.test(end)
heslog.test(timer.getAvgStep())
heslog.test(timer.getSteps())
heslog.test(end - timer.end())
