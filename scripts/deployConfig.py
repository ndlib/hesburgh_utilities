import yaml
import os
from hesburgh import heslog, hesutil
import re

# define Abort exception so we can catch it instead of the base Exception class when safely aborting
class Abort(Exception):
  pass


class Config(object):
  def __init__(self, filename, args, timestamp):
    if not os.path.isfile(filename):
      raise Abort("%s is not a valid config file" % filename)

    self.args = args
    self.timestamp = timestamp

    self.filename = filename

    with open(filename, "r") as f:
      self.config = yaml.load(f)

    self.lambdaEnvs = []
    self.stackDefs = []
    self.gateways = []

    self.replaceRe = re.compile("\${(.*)}")
    self.deployFolderStr = None


  def _singleLambdaEnv(self, env):
    environs = {}
    for var in env:
      if "Name" not in var:
        heslog.error("Trying to set variable for %s with no name" % (lambdaName))
        raise Abort("Invalid Config")

      name = self.confSub(var.get("Name"))

      if "Value" not in var:
        heslog.error("Trying to set %s for %s with no value" % (name, lambdaName))
        raise Abort("Invalid Config")

      environs[name] = self.confSub(var.get("Value"))
    return environs


  def _validateLambdaEnvs(self):
    confSection = self.config.get("LambdaEnv", {})
    defaultKey = self.confSub(confSection.get("Global", {}).get("KMSKey"))

    globalEnvs = self._singleLambdaEnv(confSection.get("Global", {}).get("Environment", []))

    for lambdaConf in confSection.get("Single", []):
      if "FunctionName" not in lambdaConf:
        heslog.error("lambda name not specified in lambdaEnv")
        raise Abort("Invalid Config")
      if not lambdaConf.get("Environment") and not globalEnvs:
        heslog.error("Trying to set lambda (%s) environ without specified variables" % lambdaConf.get("name"))
        raise Abort("Invalid Config")

      lambdaName = self.confSub(lambdaConf.get("FunctionName"))
      key = self.confSub(lambdaConf.get("KMSKey"))

      environs = self._singleLambdaEnv(lambdaConf.get("Environment", []))

      finalVars = {}
      finalVars.update(globalEnvs)
      finalVars.update(environs)
      self.lambdaEnvs.append({
        "name": lambdaName,
        "key": key or defaultKey,
        "vars": finalVars,
      })

    heslog.debug("Lambda environments: %s" % self.lambdaEnvs)


  def _validateStacks(self):
    configStacks = self.config.get("Stacks", {})
    globalTags = { k: self.confSub(v) for k,v in configStacks.get("Global", {}).get("Tags", {}).iteritems() }
    globalParams = { k: self.confSub(v) for k,v in configStacks.get("Global", {}).get("Parameters", {}).iteritems() }

    for stack in configStacks.get("Single", []):
      template = stack.get("Template")

      # either specify a template in the config or dont publish (use template on s3)
      if not template or (not self.args.noPublish and template not in self.artifactTemplates()):
        heslog.error("Template %s must be present in the Artifacts.Templates section of the config" % template)
        raise Abort("Invalid Config")

      stackName = self.confSub(stack.get("Name"))
      if not stackName:
        heslog.error("Stack requires a Name")
        raise Abort("Invalid Config")

      for gateway in stack.get("Gateways", []):
        self.gateways.append({ "name": gateway, "stack": stackName })

      localTags = { k: self.confSub(v) for k,v in stack.get("Tags", {}).iteritems() }
      localParams = { k: self.confSub(v) for k,v in stack.get("Parameters", {}).iteritems() }

      finalTags = {}
      finalTags.update(globalTags)
      finalTags.update(localTags)

      finalParams = {}
      finalParams.update(globalParams)
      finalParams.update(localParams)

      self.stackDefs.append({
        "name": stackName,
        "template": template,
        "tags": finalTags,
        "params": finalParams,
      })
    heslog.debug("Stacks: %s" % self.stackDefs)


  def _validateArtifacts(self):
    artifacts = self.config.get("Artifacts", {})
    templates = artifacts.get("Templates")

    if not templates:
      heslog.error("Config requires templates")


  def validate(self):
    if "Service" not in self.config:
      heslog.error("Config requires a 'service' field with the service name")
      raise Abort("Invalid Config")

    self.deployFolderStr = self.args.deployFolder or "$SERVICE/$STAGE/$TIMESTAMP"
    if "$DEPLOY_FOLDER" in self.deployFolderStr:
      heslog.error("Cannot use $DEPLOY_FOLDER in the deployFolder param")
      raise Abort("Invalid Config")
    self.deployFolderStr = self.confSub(self.deployFolderStr).strip('/')

    self._validateArtifacts()
    self._validateStacks()
    self._validateLambdaEnvs()


  def confSub(self, orig):
    if not orig:
      return orig

    ret = orig.replace("$SERVICE", self.serviceName())
    ret = ret.replace("$STAGE", self.args.stage)
    ret = ret.replace("$DEPLOY_BUCKET", self.args.deployBucket)
    ret = ret.replace("$DEPLOY_FOLDER", self.deployFolder())
    ret = ret.replace("$TIMESTAMP", self.timestamp)

    # we wont use any of this during deletion or publish, so don't require it
    if not self.args.delete and not self.args.publish:
      for envVal in self.replaceRe.findall(ret):
        ret = ret.replace("${%s}" % envVal, hesutil.getEnv(envVal, throw=True))
    return ret


  def setTemplateCapabilities(self, template, capabilities):
    for s in self.stackDefs:
      if s.get("template") == template:
        s["capabilities"] = capabilities


  def artifactTemplates(self):
    return self.config.get("Artifacts", {}).get("Templates", [])


  def artifactZips(self):
    return self.config.get("Artifacts", {}).get("Zips", [])


  def stacks(self):
    return self.stackDefs


  def deployFolder(self):
    return self.deployFolderStr


  def serviceName(self):
    return self.config.get("Service")


  def lambdaVars(self):
    return self.lambdaEnvs
