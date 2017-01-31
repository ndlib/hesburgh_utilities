'use strict'

var heslog = require('./heslog');

var message = "message";
heslog.debug(message);
heslog.verbose(message);
heslog.test(message);
heslog.info(message);
heslog.warn(message);
heslog.error(message);
heslog.setLevels(heslog.levels.debug, heslog.levels.error);
heslog.debug(message);
heslog.verbose(message);
heslog.test(message);
heslog.info(message);
heslog.warn(message);
heslog.error(message);
