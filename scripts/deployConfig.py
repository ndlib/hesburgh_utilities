import yaml
import os
from hesburgh import heslog, hesutil


class Config(object):
  def __init__(self, filename, args, timestamp):
    if not os.path.isfile(filename):
      raise Exception("%s is not a valid config file" % filename)

    self.args = args
    self.timestamp = timestamp

    with open(filename, "r") as f:
      self.config = yaml.load(f)

    self.lambdaEnvs = []
    self.params = {}
    self.stackTags = {}

    if not self._validate():
      raise Exception("Config validation failed")


  def _validateLambdaEnvs(self):
    valid = True
    for lambdaConf in self.config.get("lambdaEnv", []):
      environs = {}
      if "name" not in lambdaConf:
        heslog.error("lambda name not specified in lambdaEnv")
        valid = False
        continue
      if not lambdaConf.get("env"):
        heslog.error("Trying to set lambda (%s) environ without specified variables" % lambdaConf.get("name"))
        valid = False
        continue

      lambdaName = self.confSub(lambdaConf.get("name"))
      key = self.confSub(lambdaConf.get("key", None))

      for var in lambdaConf.get("env", []):
        if "name" not in var:
          heslog.error("Trying to set variable for %s with no name" % (lambdaName))
          valid = False
          continue

        name = var.get("name")

        if "env" not in var:
          heslog.error("Trying to set %s for %s with no value" % (name, lambdaName))
          valid = False
          continue

        environs[name] = hesutil.getEnv(var.get("env"), throw=True)

      self.lambdaEnvs.append({
        "name": lambdaName,
        "key": key,
        "vars": environs,
      })
    return valid


  def _validate(self):
    valid = True
    if "service" not in self.config:
      heslog.error("Config requires a 'service' field with the service name")
      valid = False

    if type(self.config.get("cloudformations")) is not list:
      heslog.error("Config requires a 'cloudformations' field of type array")
      valid = False

    for k,v in self.config.get("parameters", {}).iteritems():
      self.params[k] = self.confSub(v)

    for k,v in self.config.get("tags", {}).iteritems():
      self.stackTags[k] = self.confSub(v)

    if not self._validateLambdaEnvs():
      valid = False

    return valid


  def confSub(self, orig):
    ret = orig.replace("$SERVICE", self.serviceName())
    ret = ret.replace("$STAGE", self.args.stage)
    ret = ret.replace("$DEPLOY_BUCKET", self.args.deployBucket)
    ret = ret.replace("$DEPLOY_FOLDER", self.deployFolder())
    ret = ret.replace("$TIMESTAMP", self.timestamp)
    ret = ret.replace("$USER", hesutil.getEnv("USER", ""))
    return ret


  def stackName(self):
    if self.args.stackName:
      return self.args.stackName

    return "%s-%s" % (self.serviceName(), self.args.stage)


  def deployFolder(self):
    if self.args.deployFolder:
      return self.args.deployFolder
    return "%s/%s/%s" % (self.serviceName(), self.args.stage, self.timestamp)


  def serviceName(self):
    return self.config.get("service")


  def parameters(self):
    return self.params


  def cloudformations(self):
    return self.config.get("cloudformations")


  def tags(self):
    return self.stackTags


  def zips(self):
    return self.config.get("codeZips", {})


  def lambdaVars(self):
    return self.lambdaEnvs
