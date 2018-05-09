#!/usr/bin/env python
import argparse
import sys
import signal

from datetime import datetime

import deployConfig
from deployConfig import Abort
from hesburgh import heslog, hesutil

import lifecycle

timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")

# check arguments to ensure those mutually exclusive with "current" are not also present if "current" is present
def _argExcludes(args, current, *excludes):
  hasCurrent = vars(args).get(current)
  if not hasCurrent:
    return True

  for e in excludes:
    if vars(args).get(e):
      heslog.error("Invalid argument combination passed %s and %s" % (current, e))
      return False
  return True

# check arguments to ensure those required by "current" are also present if "current" is present
def _argRequres(args, current, *requires):
  hasCurrent = vars(args).get(current)
  if not hasCurrent:
    return True

  for e in requires:
    if not vars(args).get(e):
      heslog.error("Arguments invalid: %s requires specifying %s" % (current, e))
      return False
  return True


# validate mutually exclusive / required arguments
def validateArgs(args):
  return (
        _argExcludes(args, "pre", "noPre")
    and _argExcludes(args, "post", "noPost")
    and _argExcludes(args, "publish", "noPublish", "noAws")
    and _argExcludes(args, "env", "noAws")
    and _argExcludes(args, "noPublish", "keepLocal")
    and _argExcludes(args, "create", "update", "delete", "replace", "noAws")
    and _argExcludes(args, "update", "create", "delete", "replace", "noAws")
    and _argExcludes(args, "replace", "create", "delete", "update", "noAws")
    and _argExcludes(args, "delete", "create", "update", "replace", "noAws", "pre", "post", "publish", "env")
    and _argExcludes(args, "verbose", "debug")
    and _argExcludes(args, "listStages", "pre", "post", "create", "update", "delete", "replace", "noAws", "publish", "env", "keepLocal")

    and _argRequres(args, "noPublish", "deployFolder")
    and _argRequres(args, "yes", "stage")
  )

# gracefully handle ctrl+c
def ctrlC(signal, frame):
  raise Abort("Ctrl-C")


def main():
  signal.signal(signal.SIGINT, ctrlC)

  heslog.addContext(stage="init")

  parser = argparse.ArgumentParser()
  parser.add_argument('--stage', '-s', type=str, default="",
    help='The stage to deploy to. Must only contain alpha-numeric ascii characters')
  parser.add_argument('--config', '-c', type=str,
    help='Config file to use as input (default is config.yml)')

  # override defaults
  parser.add_argument('--deployBucket', type=str, default="testlibnd-cf",
    help='The bucket the artifacts will be put into (default is testlibnd-cf)')
  parser.add_argument('--deployFolder', type=str,
    help='Override the deployment folder (default is $SERVICE/$STAGE/$TIMESTAMP)')
  parser.add_argument('--useServiceRole', action='store_true', dest='useServiceRole', default=False,
    help='Pass the service role to cloudformation for stack actions (defaults to false)')

  # specify steps to do
  parser.add_argument('--pre', action='store_true',
    help="Do pre-deploy step (excludes all other steps, addative with other step flags)")
  parser.add_argument('--post', action='store_true',
    help="Do post-deploy step (excludes all other steps, addative with other step flags)")
  parser.add_argument('--publish', action='store_true',
    help="Do the publish step (excludes all other steps, addative with other step flags)")
  parser.add_argument('--env', action='store_true',
    help="Do the lambda environment update step (excludes all other steps, addative with other step flags)")

  # specify steps to skip
  parser.add_argument('--noPre', action='store_true',
    help="Skip pre-deploy step")
  parser.add_argument('--noPost', action='store_true',
    help="Skip post-deploy step")
  parser.add_argument('--noPublish', action='store_true',
    help="Don't create or publish artifacts (CF, code zip, etc) NOTE: You must override deployFolder if you specify this argument")
  parser.add_argument('--noEnv', action='store_true',
    help="Skip the lambda environment update step")

  # specify stack interaction
  parser.add_argument('--create', action='store_true',
    help="Create stack if it doesn't exist")
  parser.add_argument('--update', action='store_true',
    help="Update stack if it exists, otherwise error and quit")
  parser.add_argument('--replace', action='store_true',
    help="Tear down existing stack if it exists and create a new one with the same stage name")
  parser.add_argument('--delete', action='store_true',
    help="Delete the stack(s)")

  # Other configuration
  parser.add_argument('--noAws', action='store_true',
    help="Don't interact with aws at all")
  parser.add_argument('--keepLocal', action='store_true',
    help="Don't delete locally created artifacts on completion")

  # single command - exits
  parser.add_argument('--listStages', action='store_true',
    help="Lists all existing stages for the project, exits on completion")

  # force no interaction
  parser.add_argument('--yes', '-y', action='store_true',
    help="Yes to all prompts (no interaction)")

  # Logging
  parser.add_argument('--verbose', action='store_true',
    help="Verbose output")
  parser.add_argument('--debug', action='store_true',
    help="Debug output")

  args = parser.parse_args()

  # make sure only valid combinations are passed
  if not validateArgs(args):
    sys.exit(1)

  if args.debug:
    heslog.setLevels()
  elif args.verbose:
    heslog.setLevels(heslog.LEVEL_INFO, heslog.LEVEL_WARN, heslog.LEVEL_ERROR, heslog.LEVEL_VERBOSE)
  else:
    heslog.setLevels(heslog.LEVEL_INFO, heslog.LEVEL_WARN, heslog.LEVEL_ERROR)

  timer = hesutil.Timer(True)

  try:
    config = deployConfig.Config(args, timestamp)

    life = lifecycle.Lifecycle(args, config, timer)
    life.run()

    heslog.info("Total Time: %s" % timer.end())
  except Abort as e:
    heslog.info("Aborting due to %s" % e)
    sys.exit(1)

  if life.deployFailure:
    sys.exit(1)


if __name__ == "__main__":
  main()

