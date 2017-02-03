from hesburgh import heslog

message = "message"

heslog.debug(message)
heslog.verbose(message)
heslog.info(message)
heslog.warn(message)
heslog.error(message)

heslog.setLevels(heslog.LEVEL_DEBUG, heslog.LEVEL_ERROR)

heslog.debug(message)
heslog.verbose(message) # should not print
heslog.info(message) # should not print
heslog.warn(message) # should not print
heslog.error(message)
