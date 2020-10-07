# CloudGuruChallenge – Event-Driven Python on AWS

Here lies the source to my solution to [this challenge](https://acloudguru.com/blog/engineering/cloudguruchallenge-python-aws-etl). A write-up on my approach to this can be found in `this blog post`

## Deploying the Stack

<span><</span>shamelessPlug<span>></span>

I prefer to use [my own tooling](https://github.com/fireflycons/PSCloudFormation) to deploy CloudFormation from the command line as it's a _sooo_ much better experience than aws cli!

<span><</span>/shamelessPlug<span>></span>

1. Clone the repo
1. Set up a virtual env and activate it (see below)
1. Deploy the entire stack including local python files with a single line of PowerShell
1. Upload the two files in the `presentation` directory to the root of the bucket created by the stack

### Python venv configuration

```bash
python -m venv venv
pip install boto3 gviz_api crhelper requests
```

### Building the Stack

If you intend to supply a custom CNAME for the CloudFront distribution created by the stack, you will need to create a [parameter file](https://github.com/fireflycons/PSCloudFormation/blob/master/docs/en-US/New-PSCFNStack.md#-parameterfile) for the relevant stack parameters.

```powershell
New-PSCFNPackage -TemplateFile cloudFormation.yaml | New-PSCFNStack -StackName acg-challenge -Capabilities CAPABILITY_IAM,CAPABILITY_AUTO_EXPAND [-ParameterFile optional-params.yaml]
```

