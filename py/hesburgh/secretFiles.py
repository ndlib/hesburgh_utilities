import argparse
import yaml
import json
import boto3
import copy
import paramiko
import os
from datetime import datetime

# To get factotum development secrets:
# a python secretFiles.py -p factotum -f secrets get -s development > config/secrets.yml
# a python secretFiles.py -p factotum -f database get -s development ddw_development > config/database.yml

# /all/[project]/[stage]/[file]/...
basePath = "/all/%s/%s/%s"

client = None

# "defaults" stage will be included in all other top-level keys unless overriden
# /all/factotum/default/secrets/ldap/service_dn = secret

# /all/factotum/development/secrets/secret_key_base = secret

def confirm(msg):
  val = raw_input(msg)
  return val.lower() == "y"

# connect to aws ssm:
# dev should be using an aws role while other processes(eg jenkins)
# could be passing credentials with strictly configured access 
def setupClient(args):
  if args.awsKey1 is None:
    return boto3.client('ssm')
  else:
    return boto3.client(
      'ssm',
      region_name='us-east-1',
      aws_access_key_id=args.awsKey1,
      aws_secret_access_key=args.awsKey2
    )

def epoch():
  return (datetime.now() - datetime.utcfromtimestamp(0)).total_seconds()

# get secrets under specified path and populate valueDict with them
# returns if there were any new values
def pathIntoDict(path, valueDict):
  next_token = ''
  params = []
  while next_token is not None:
    if next_token == '':
      response = client.get_parameters_by_path(
                    Path=path,
                    Recursive=True,
                    WithDecryption=True
                  )
      params = response.get("Parameters")
    else:
      response = client.get_parameters_by_path(
                    Path=path,
                    Recursive=True,
                    WithDecryption=True,
                    NextToken=next_token
                  )
      params_page = response.get("Parameters")
      params.extend(params_page)

    next_token = response.get('NextToken', None)

  for p in params:
    writeInto = valueDict

    name = p.get("Name")

    # cut off /all/[project]/[stage]/[file]/
    split = name.split('/')[5:]

    # make sure we're writing utf8, not unicode
    for i in xrange(len(split)):
      split[i] = split[i].encode('utf8')

    # make the tree depth
    while len(split) > 1:
      if split[0] not in writeInto:
        writeInto[split[0]] = {}
      writeInto = writeInto[split[0]]
      split.pop(0)

    # make sure we're writing utf8, not unicode
    value = p.get("Value").encode('utf8')
    if p.get("Type") == "StringList":
      value = value.split(',')

    writeInto[split[0]] = value

  return len(params) > 0


def getSecrets(args):
  toWrite = {}
  defaults = {}

  path = basePath % (args.project, "default", args.file)
  pathIntoDict(path, defaults)

  hasValues = False
  for stage in args.stages:
    # start with defaults, they'll be overwritten automatically
    toWrite[stage] = copy.deepcopy(defaults)

    path = basePath % (args.project, stage, args.file)
    currentValues = pathIntoDict(path, toWrite[stage])
    hasValues = hasValues or currentValues
    
  if not hasValues:
    if not confirm("There are no secrets in the given file, continue with output? [Y|N] >> "):
      print "Exiting"
      return
    else:
      print "# Any values present will be from defaults"

  formattedData = formatOutput(toWrite, args.output)
  if args.upload:
    print "Uploading %s to %s" % (args.file, args.upload)
    tmpFileName = "tmp_%s" % epoch()

    with open(tmpFileName, 'w') as f:
      f.write(formattedData)

    try:
      # connect to server
      ssh = paramiko.SSHClient()
      ssh.load_system_host_keys()
      ssh.connect(hostname=args.upload, username="app")

      # upload
      ftp = ssh.open_sftp()
      remotePath = "/home/app/%s/shared/config/%s.yml" % (args.project, args.file)
      ftp.put(tmpFileName, remotePath)

      if args.restart:
        # restart passenger
        touch = "touch /home/app/%s/current/tmp/restart.txt" % (args.project)
        print "Restarting %s on %s" % (args.project, args.upload)
        ssh.exec_command(touch)

    except Exception as e:
      print e

    # cleanup tmp file
    os.remove(tmpFileName)
  else:
    print formattedData


def makeSecret(args):
  path = basePath % (args.project, args.stage, args.file)
  path += "/" + args.key

  isList = raw_input("Is the secret a list? [Y|N] >> ")
  paramType = "SecureString"
  value = None

  # get the secret value
  if isList.lower() == "y":
    paramType = "StringList"
    value = []

    # get every element
    while True:
      element = raw_input("Element in list? (:q to quit) >> ")
      if element == ":q":
        break
      value.append(element)
    # make the list a string
    value = ",".join(value)
  else:
    value = raw_input("What is the secret value? >> ")

  print "Creating %s" % path
  client.put_parameter(
    Name=path,
    Value=value,
    Type=paramType
  )


def deleteSecret(args):
  path = basePath % (args.project, args.stage, args.file)
  path += "/" + args.key

  print "Deleting %s" % path
  client.delete_parameter(
    Name=path
  )

# output yaml(default) or map formatted parameters
def formatOutput(toWrite, outputFormat):
  output = ""
  if outputFormat:
    for key, value in toWrite.iteritems():
      # print stage
      print str(key)
      for k,v in value.iteritems():
        # print key and value
        print  str(k) + "=" + str(v)
  else:
    output = yaml.dump(toWrite, default_flow_style=False)
  return output

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--project', '-p', type=str, required=True,
    help="Project to read/write (eg. factotum)")
  parser.add_argument('--file', '-f', type=str, required=True,
    help="File name to read/write")
  parser.add_argument('--awsKey1', '-ak1', type=str, help="AWS access key")
  parser.add_argument('--awsKey2', '-ak2', type=str, help="AWS secret access key")

  subparsers = parser.add_subparsers()

  get = subparsers.add_parser('get', help='Get secret files')
  get.set_defaults(func=getSecrets)
  get.add_argument('--stages', '-s', type=str, nargs="+", required=True,
    help="Stages to get (development, production, etc)")
  get.add_argument('--upload', '-u', type=str,
    help="The address of the machine to upload to")
  get.add_argument('--restart', action="store_true",
    help="Touch the restart file after upload to server")
  get.add_argument('--output', '-o', type=str,
    help="Parameter output format(yaml(default), map)")

  create = subparsers.add_parser('update', help='Create or Update a secret')
  create.set_defaults(func=makeSecret)
  create.add_argument('--key', '-k', type=str, required=True,
    help="Key of the secret to set")
  create.add_argument('--stage', '-s', type=str, required=True,
    help="Stage to write (development, production, etc)")

  delete = subparsers.add_parser('delete', help='Delete secret')
  delete.set_defaults(func=deleteSecret)
  delete.add_argument('--stage', '-s', type=str, required=True,
    help="Stage of the key (development, production, etc)")
  delete.add_argument('--key', '-k', type=str, required=True,
    help="Key of the secret to delete")
  
  args = parser.parse_args()

  # connect to aws ssm
  global client
  client = setupClient(args)
  args.func(args)

if __name__ == "__main__":
  main()
