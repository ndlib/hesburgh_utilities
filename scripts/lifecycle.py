import boto3
from botocore.exceptions import ClientError

import os
import base64
import re
import time
import sys

from deployConfig import Abort
from hesburgh import heslog, hesutil, scriptutil
import deployHelpers


# TODO:
#   use changesets instead of straight deploy commands
#   run pre-deploy scripts
#   run post-deploy scripts


# make sure given stage contains valid characters
validStagePattern = re.compile("^[a-zA-Z0-9]*$")

class Lifecycle(object):
  def __init__(self, args, config, timer):
    self.args = args
    self.config = config
    self.timer = timer
    self.deployFailure = False

    self.encrypted = {}

    self.deployDir = "deploy_%s" % self.config.timestamp

    self.stackFnKey = '_stack_fn_'
    self.deploymentStepOrder = [
      {
        "key": "pre",
        "fn": self.preDeploy,
      },
      {
        "key": "publish",
        "fn": self.publish,
      },
      {
        "key": self.stackFnKey,
        "fn": lambda: self.stackAction.get("fn")(),
      },
      {
        "key": "env",
        "fn": self.envUpdate,
      },
      {
        "key": "post",
        "fn": self.postDeploy,
      }
    ]
    self.stackAction = None
    self.steps = []

    self.cfClient = None
    if not self.args.noAws:
      self.cfClient = boto3.client('cloudformation')


  # Used to check if any of the specified "exitOn" args were passed in as cli args
  def _shouldRunByArgs(self, name, *exitOn):
    for e in exitOn:
      if vars(self.args).get(e):
        heslog.info("Skipping %s because '%s' was specified" % (name, e))
        return False
    return True


  def _encrypt(self, kmsKey, key, val):
    if kmsKey and key not in self.encrypted:
      try:
        heslog.verbose("Encrypting %s" % key)

        client = boto3.client('kms')
        response = client.encrypt(
          KeyId=kmsKey,
          Plaintext=val,
        )
        self.encrypted[key] = base64.b64encode(response.get("CiphertextBlob")).decode("utf-8")
      except Exception as e:
        heslog.error(e)
        raise Abort("Encryption Error")

    elif key not in self.encrypted:
      self.encrypted[key] = val

    return self.encrypted[key]


  def _updateLambda(self, func, env, kmsKey):
    heslog.info("Updating lambda '%s'" % func)

    env = { k: self._encrypt(kmsKey, k, v) for k,v in env.iteritems() }

    try:
      client = boto3.client('lambda')
      # Get the current environment so we don't lose things we're not overwriting
      response = client.get_function_configuration(FunctionName=func)
      currentEnv = response.get("Environment", {}).get("Variables", {})
      currentEnv.update(env)
      heslog.debug(currentEnv)

      response = client.update_function_configuration(
        FunctionName=func,
        Environment={
          'Variables': currentEnv
        },
      )
    except ClientError as e:
      heslog.error(e)


  def _deployGateway(self, gatewayInfo):
    gateway = gatewayInfo.get("name")
    stackName = gatewayInfo.get("stack")
    heslog.info("Deploying Gateway from Stack: %s Name: %s" % (stackName, gateway))

    try:
      response = self.cfClient.describe_stacks(
        StackName=stackName
      )

      outputs = response.get("Stacks")[0].get("Outputs", {})
      for i in outputs:
        if i.get("OutputKey", "") == gateway:
          apiId = i.get("OutputValue")
          break

      if not apiId:
        heslog.error("Gateway %s could not be found in outputs of %s" (gateway, stackName))
        return

      description = "Hesdeploy %s" % (self.config.deployFolder() if not self.args.env else "env")

      client = boto3.client("apigateway")
      client.create_deployment(
        restApiId=apiId,
        stageName=self.args.stage,
        description=description
      )
    except Exception as e:
      heslog.error(e)


  def preDeploy(self):
    heslog.addContext(stage="preDeploy")

    if self._shouldRunByArgs("template validation", "noAws"):
      file = "_"
      try:
        heslog.info("Validating Templates")
        for file in self.config.artifactTemplates():
          heslog.verbose("Validating %s" % file)
          with open(file) as f:
            response = self.cfClient.validate_template(TemplateBody=f.read())
            self.config.setTemplateCapabilities(file, response.get("Capabilities", []))
      except Exception as e:
        heslog.error(e)
        raise Abort("Validation Failure on %s" % file)

    if self._shouldRunByArgs("artifact creation", "noPublish"):
      if self.config.artifactZips():
        os.mkdir(self.deployDir)


  def package(self):
    heslog.addContext(stage="package")
    heslog.info("Creating artifacts")

    for zipConf in self.config.artifactZips():
      deployHelpers.makeZip("%s/%s.zip" % (self.deployDir, zipConf.get("Name")), zipConf.get("Files"))
    heslog.info("Finished zipping in %ss" % (self.timer.step(True)))


  def publish(self):
    if self._shouldRunByArgs("publish steps", "noPublish"):
      self.package()

      heslog.addContext(stage="publish")
      try:
        if self._shouldRunByArgs("publishing files", "noAws"):
          client = boto3.client('s3')
          heslog.info("Publishing to s3://%s/%s" % (self.args.deployBucket, self.config.deployFolder()))

          heslog.info("Uploading config file")
          heslog.verbose("Upload %s => s3://%s/%s/%s" % (self.config.filename, self.args.deployBucket, self.config.deployFolder(), self.config.filename))
          client.upload_file(self.config.filename, self.args.deployBucket, '%s/%s' % (self.config.deployFolder(), self.config.filename))

          heslog.info("Uploading artifact templates")
          for file in self.config.artifactTemplates():
            heslog.verbose("Upload %s => s3://%s/%s/%s" % (file, self.args.deployBucket, self.config.deployFolder(), file))
            client.upload_file(file, self.args.deployBucket, '%s/%s' % (self.config.deployFolder(), file))

          if os.path.exists(self.deployDir):
            heslog.info("Uploading artifact zips")
            for realPath, filename in deployHelpers.walk(self.deployDir):
              heslog.verbose("Upload %s => s3://%s/%s/%s" % (realPath, self.args.deployBucket, self.config.deployFolder(), filename))
              client.upload_file(realPath, self.args.deployBucket, '%s/%s' % (self.config.deployFolder(), filename))

          heslog.info("Finished publishing in %ss" % (self.timer.step(True)))
      except Exception as e:
        heslog.error(e)
        raise Abort("Publish Error")


  def createStacks(self):
    heslog.addContext(stage="createStacks")
    if self._shouldRunByArgs("cloudformation", "publish", "env"):
      for stackConfig in self.config.stacks():
        if self.deployFailure:
          heslog.warn("Breaking due to DeployFailure")
          break
        self._createSingleStack(stackConfig)


  def updateStacks(self):
    heslog.addContext(stage="updateStacks")
    for stackConfig in self.config.stacks():
      if self.deployFailure:
        heslog.warn("Breaking due to DeployFailure")
        break
      self._updateSingleStack(stackConfig)


  def replaceStacks(self):
    heslog.addContext(stage="replaceStacks")
    for stackConfig in self.config.stacks():
      if self.deployFailure:
        heslog.warn("Breaking due to DeployFailure")
        break
      self._replaceSingleStack(stackConfig)


  def deleteStacks(self):
    heslog.addContext(stage="deleteStacks")
    for stackConfig in self.config.stacks():
      self._deleteSingleStack(stackConfig)


  def createOrUpdateStacks(self):
    heslog.addContext(stage="createOrUpdateStacks")
    for stackConfig in self.config.stacks():
      if self.deployFailure:
        heslog.warn("Breaking due to DeployFailure")
        break

      if self._stackExists(stackConfig.get("name")):
        self._updateSingleStack(stackConfig)
      else:
        self._createSingleStack(stackConfig)


  def _stackArgs(self, stackConfig):
    stackName = stackConfig.get("name")
    path = self.config.deployFolder()
    template = stackConfig.get("template")
    rootTemplate = "https://s3.amazonaws.com/%s/%s/%s" % (self.args.deployBucket, path, template)

    params = [ { "ParameterKey": k, "ParameterValue": v } for k,v in stackConfig.get("params").iteritems() ]
    tags = [ { "Key": k, "Value": v } for k,v in stackConfig.get("tags").iteritems() ]

    stackArgs = {
      "StackName": stackName,
      "TemplateURL": rootTemplate,
      "Parameters": params,
      "Capabilities": stackConfig.get("capabilities"),
      "Tags": tags,
    }
    heslog.verbose("Stack args %s" % stackArgs)
    return stackArgs


  def _stackExists(self, stackName):
    try:
      response = self.cfClient.describe_stacks(
        StackName=stackName
      )
      return response.get("Stacks", [])[0].get("StackId")
    except ClientError:
      return None


  def _replaceSingleStack(self, stackConfig):
    self._deleteSingleStack(stackConfig)
    self._createSingleStack(stackConfig)


  def _createSingleStack(self, stackConfig):
    stackName = stackConfig.get("name")

    heslog.addContext(stackName=stackName)
    stackArgs = self._stackArgs(stackConfig)
    template = stackConfig.get("template")

    if self._shouldRunByArgs("running cloudformation for %s" % template, "noAws"):
      if self._stackExists(stackName):
        heslog.removeContext("stackName")
        raise Abort("Cannot create existing stack %s" % stackName)

      try:
        heslog.info("Creating Stack '%s' with %s" % (stackName, template))
        response = self.cfClient.create_stack(**stackArgs)
        self.waitCreate(response.get("StackId"))
      except ClientError as e:
        heslog.error(e)
        self.deployFailure = True

      heslog.info("CF Finished in %ss" % (self.timer.step(True)))
    heslog.removeContext("stackName")


  def _updateSingleStack(self, stackConfig):
    stackName = stackConfig.get("name")

    heslog.addContext(stackName=stackName)
    stackArgs = self._stackArgs(stackConfig)
    template = stackConfig.get("template")

    if self._shouldRunByArgs("running cloudformation for %s" % template, "noAws"):
      if not self._stackExists(stackName):
        heslog.removeContext("stackName")
        raise Abort("Cannot update non-existing stack %s" % stackName)

      try:
        heslog.info("Updating Stack '%s' with %s" % (stackName, template))
        response = self.cfClient.update_stack(**stackArgs)
        self.waitUpdate(response.get("StackId"))
      except ClientError as e:
        heslog.error(e)
        self.deployFailure = True
      heslog.info("CF Finished in %ss" % (self.timer.step(True)))

    heslog.removeContext("stackName")


  def _deleteSingleStack(self, stackConfig):
    stackName = stackConfig.get("name")
    heslog.addContext(stackName=stackName)
    stackId = self._stackExists(stackName)

    if not stackId:
      heslog.removeContext("stackName")
      return

    if self._shouldRunByArgs("stack delete", "noAws"):
      heslog.info("Deleting stack %s" % stackName)
      response = self.cfClient.delete_stack(
        StackName=stackName,
      )

      self.waitDelete(stackId)
      heslog.info("Deleted stack in %s" % (self.timer.step(True)))

    heslog.removeContext("stackName")


  def envUpdate(self):
    heslog.addContext(stage="envUpdate")

    if (self._shouldRunByArgs("lambda update", "noAws", "publish")
        and len(self.config.lambdaVars()) > 0
        and not self.deployFailure):
      for lambdaConf in self.config.lambdaVars():
        self._updateLambda(lambdaConf.get("name"), lambdaConf.get("vars", {}), lambdaConf.get("key"))
      heslog.info("Finished Updating Lambdas in %ss" % (self.timer.step(True)))


  def postDeploy(self):
    heslog.addContext(stage="postDeploy")

    if (self._shouldRunByArgs("api deploy", "noAws", "publish")
        and not self.deployFailure
        and len(self.config.gateways) > 0):
      for gatewayInfo in self.config.gateways:
        self._deployGateway(gatewayInfo)
      heslog.info("Finshed Deploying Gateways in %ss" % (self.timer.step(True)))

    # remove temp directory
    if self._shouldRunByArgs("delete local artifacts", "keepLocal") and os.path.exists(self.deployDir):
      for root, dirs, files in os.walk(self.deployDir):
        for file in files:
          heslog.verbose("Removing tmp file %s/%s" % (root, file))
          os.remove(os.path.join(root, file))
      heslog.verbose("Removing tmp dir %s" % self.deployDir)
      os.rmdir(self.deployDir)


  def getStages(self, service):
    statusFilter = [
      'CREATE_IN_PROGRESS',
      'CREATE_FAILED',
      'CREATE_COMPLETE',
      'ROLLBACK_IN_PROGRESS',
      'ROLLBACK_FAILED',
      'ROLLBACK_COMPLETE',
      'UPDATE_IN_PROGRESS',
      'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS',
      'UPDATE_COMPLETE',
      'UPDATE_ROLLBACK_IN_PROGRESS',
      'UPDATE_ROLLBACK_FAILED',
      'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
      'UPDATE_ROLLBACK_COMPLETE',
      'REVIEW_IN_PROGRESS',
    ]

    token = False
    stages = []

    commandArgs = {
      "StackStatusFilter": statusFilter,
    }

    # None is returned for the token by the api when we hit the end
    while token is not None:
      response = {}
      response = self.cfClient.list_stacks(**commandArgs)

      for stack in response.get("StackSummaries", []):
        stackName = stack.get("StackName")
        if stackName.startswith(self.config.serviceName()):
          subStr = stackName[len(self.config.serviceName()) + 1:]

          # don't want sub-stacks (eg: gatekeeper-dev-RolesStack)
          if subStr.count('-') == 0:
            stages.append(subStr)

      token = response.get("NextToken")
      commandArgs["NextToken"] = token

    return stages


  def _inputNewStage(self):
    heslog.info("Input a new stage to create using only alpha-numeric characters")
    while True:
      givenStage = scriptutil.userInput("Stage Name")
      if not validStagePattern.match(givenStage):
        heslog.error("For the safety of any templates it is passed to, 'stage' must only contain alpha-numeric characters")
      else:
        self.args.stage = givenStage
        return


  def selectStageTouse(self, stages):
    if len(stages) <= 0:
      heslog.info("No stages found for %s" % self.config.serviceName())
      return self._inputNewStage()

    validIndicies = [ str(i) for i in xrange(len(stages)) ]
    validIndicies.append('n')

    while True:
      heslog.info("Please select a stage for %s:" % self.config.serviceName())
      for i in xrange(len(stages)):
        heslog.info(" %s: %s" % (i, stages[i]))
      heslog.info(" n: Create New Stage")

      selected = scriptutil.getValidInput("Select stage",  validIndicies)

      if selected == 'n':
        return self._inputNewStage()

      heslog.info("Selected stage %s" % self.args.stage)
      if scriptutil.isTruthy(scriptutil.userInput("Is this correct? [Y|N]")):
        self.args.stage = stages[int(selected)]


  def setStepsToRun(self, existingStages):
    # determine if we are limiting the steps because some were specified
    for s in self.deploymentStepOrder:
      stepName = s.get("key")
      if vars(self.args).get(stepName):
        self.steps.append(stepName)

    # if a step is specified, we want to exclude all other non-specified steps
    isExlusive = len(self.steps) > 0
    # otherwise, do all steps
    if not isExlusive:
      self.steps = [ s.get("key") for s in self.deploymentStepOrder ]

    possibleStackSteps = [
      {
        "key": "create",
        "fn": self.createStacks,
      },
      {
        "key": "update",
        "fn": self.updateStacks,
      },
      {
        "key": "replace",
        "fn": self.replaceStacks,
      },
      {
        "key": "delete",
        "fn": self.deleteStacks,
      },
    ]

    # determine if the stack func was specified
    if not self.args.noAws:
      for s in possibleStackSteps:
        if vars(self.args).get(s.get("key")):
          heslog.debug("setting update func to %s" % s.get("key"))
          self.stackAction = s

          if self.stackFnKey not in self.steps:
            self.steps.append(self.stackFnKey)
          break

      # if no stack func is specified, and we're not excluding steps, do create or update
      if self.stackAction is None and not isExlusive:
        self.stackAction = { "key": "CreateOrUpdate", "fn": self.createOrUpdateStacks }

    # if nothign set the stackAction, just do a no op
    if self.stackAction is None:
      self.stackAction = { "key": "NoOp", "fn": deployHelpers.NOOP }

    heslog.debug("running steps %s" % self.steps)


  # Run the entire deployment
  def run(self):
    try:
      # Make sure we assumed a role if needed
      if not self.args.noAws and not hesutil.getEnv("AWS_ROLE_ARN"):
        heslog.error("When 'noAws' has not been specified you must assume a role to run this script")
        raise Abort('No Assumed Role')

      stages = []
      if not self.args.noAws:
        stages = self.getStages(self.config.serviceName())

      # If we're just listing existing stages, do so
      if self.args.listStages:
        heslog.info("Existing stages for %s:" % self.config.serviceName())
        for s in stages:
          heslog.info("  %s" % s)
        return

      if self.args.stage and not validStagePattern.match(self.args.stage):
        heslog.error("For the safety of any templates it is passed to, 'stage' must only contain alpha-numeric characters")
        raise Abort("Paramter Validation")

      # Set the steps of deployment to run based on given args
      self.setStepsToRun(stages)

      if not self.args.noAws:
        # If we don't have a stage, prompt user to select an existing one or create a new one
        if not self.args.stage and self.stackFnKey in self.steps:
          self.selectStageTouse(stages)

        # confirm stack action on stage
        if self.stackFnKey in self.steps:
          if not scriptutil.isTruthy(scriptutil.userInput("%s stage '%s'? [Y|N]" % (self.stackAction.get("key"), self.args.stage))):
            raise Abort("Canceled Stack Action")


      # We should now have a stage selected, which means we can validate the config file
      self.config.validate()

      for step in self.deploymentStepOrder:
        if step.get("key") in self.steps or step == self.stackFnKey:
          fn = step.get("fn")
          fn()

    except (Abort, ClientError) as e:
      heslog.setContext({})
      heslog.info("Aborting due to %s" % e)
      sys.exit(1)
    heslog.setContext({})


  ############ CF WAIT, use this instead of given waiters so we can output '....' to show progress
  def CFWait(self, stackId, doneState, progressState):
    try:
      while True:
        sys.stdout.write(".")
        sys.stdout.flush()
        response = self.cfClient.describe_stacks(
          StackName=stackId
        )

        stack = response.get("Stacks", [])[0]
        status = stack.get("StackStatus")
        # use startswith because "update_complete_clenaup_in_progress"
        # is also a valid done state
        if status.startswith(doneState):
          #newline
          print
          return True
        elif status != progressState:
          self.deployFailure = True
          #newline
          print
          if status == "ROLLBACK_IN_PROGRESS":
            heslog.error(stack.get("StackStatusReason"))
          else:
            # Likely want to handle the other non-success statuses eventually
            # But this at least gives us the needed information
            print status
            print stack.get("StackStatusReason")
          return False

        time.sleep(10)
    except Exception as e:
      heslog.error("While Waiting %s " % e)


  def waitCreate(self, stackId):
    if self.CFWait(stackId, "CREATE_COMPLETE", "CREATE_IN_PROGRESS"):
      heslog.info("Stack Creation Complete")


  def waitUpdate(self, stackId):
    if self.CFWait(stackId, "UPDATE_COMPLETE", "UPDATE_IN_PROGRESS"):
      heslog.info("Stack Update Complete")


  def waitDelete(self, stackId):
    if self.CFWait(stackId, "DELETE_COMPLETE", "DELETE_IN_PROGRESS"):
      heslog.info("Stack Delete Complete")


