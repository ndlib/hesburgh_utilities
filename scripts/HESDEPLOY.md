# hesdeploy

This script is used to deploy cloudformations in a common, easy fashion

It will:
- Validate your cloudformation templates using the AWS template validator
- Zip code artifacts
- Publish code + templates to S3
- Deploy defined stack(s)
- Update any lambda environments with encrypted values

## Config
You must have a config file with infomation about the stack(s) and file(s) you'll be deploying, here is an [Example](example.yml) with every option filled in.

The above example has all possible fields for visibility. Here is the most basic required configuration file:
```
Service: serviceName

Stacks:
  Single:
    - Name: stackname
      Template: root.yml

Artifacts:
  Templates:
    - root.yml
```
The `Stacks.Single` section is, perhaps badly named, a list of (possibly one) stack(s) to create. This is where the stack name and template to use are defined, as well as any specific stack parameters or tags. Any Parameters or tags to be used on all stacks should be located under the optional `Stacks.Global` section.

The `Artifacts.Templates` section defines the cloudformation template files to be validated and published to S3. The `Template` parameter under each stack in `Stacks.Single` must be a filename present in this list (unless `--noPublish` is specified, as in that case we assume the template file is already valid and in the specified S3 deployBucket). This section does NOT define stacks to be created, only cloudformations to validate and publish.

Any variables like `${FOO}` is assumed to be an environment variable and if it's not found hesdeploy will fail

There are variables accessable in the config that are generated from the deployments script. These are denoted with a preceding $ without the {} braces.

| Key         | Value
|-------------|------------
| SERVICE     | The service name (the one given at the top of the config)
| STAGE       | The stage being deployed (given by --stage)
| DEPLOY_BUCKET | The name of the bucket being deployed to
| DEPLOY_FOLDER | The path in the bucket artifacts will be published into
| TIMESTAMP   | The timestamp of this deployment

These can be chained with eachother and with environment variables, for instance `${USER}-$STAGE-test` with stage `dev` and USER env val `hbeachey` will produce `hbeachey-dev-test`

## Usage

After assuming the required role and sourcing required secrets files, the most basic usage is as follows:
```
hesdeploy -s [stage]
```

## Options
| Option      | Parameter  | Description
|-------------|------------|------------
| --help, -h   |            | Show the help message
| --stage, -s  | stage      | The stage to deploy to (eg. dev). Must only contain alpha-numeric ascii characters
| --config, -c | config     | Config file to use as input (default is config.yml)
| --deployBucket | bucketName | The bucket the artifacts will be put into (default is testlibnd-cf)
| --deployFolder | folder    | Override the deployment folder (default is $SERVICE/$STAGE/$TIMESTAMP)
| --delete      |           | Delete the stack(s)
| --publishOnly |           | Publish files to the S3 bucket without calling the CF files
| --envOnly    |            | Update lambda environment(s) without publishing/deploying
| --noPublish  |            | Don't create or publish artifacts (CF, code zip, etc) NOTE: You must override deployFolder if you specify this argument
| --noAws      |            | Don't interact with aws at all
| --keepLocal  |            | Don't delete locally created artifacts on completion
| --verbose    |            | Verbose output
| --debug      |            | Debug output


## Tech Notes
All parsing of the config file, environment variables and validation of clouformation tempaltes is done before anything is pushed to AWS. This allows early failure so we don't have to wait for half the stack to be created before we hit an error. Of course, this doesn't fix every case, but it should catch very common cases.
