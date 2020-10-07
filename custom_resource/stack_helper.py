# https://github.com/aws-cloudformation/custom-resource-helper
import boto3
from crhelper import CfnResource


helper = CfnResource()

def empty_website_bucket(bucket_name):
    """
    Empties the website bucket.
    """
    bucket = boto3.resource('s3').Bucket(bucket_name)
    to_delete = [{ 'Key': o.key } for o in bucket.objects.all()]

    if not to_delete:
        # Bucket aleady empty
        return

    bucket.delete_objects(
        Delete={
            'Objects': to_delete
        }
    )


def invoke_etl(function_arn):
    try:
        boto3.client('lambda').invoke(
            FunctionName=function_arn,
            InvocationType='Event'
        )
    except Exception as e:
        # Not fatal
        print(f'Unable to invoke ETL lambda: {e}')


@helper.create
def on_create(event, _):
    """
    Handle Custom Resouce create event.
    Invoke ETL to load the initial dataset.
    """
    pass
    invoke_etl(event['ResourceProperties']['ETLFunction'])


@helper.update
def on_update(_, __):
    """
    Handle Custom Resouce update event.
    Do nothing here.
    """
    pass


@helper.delete
def on_delete(event, _):
    """
    Handle Custom Resouce delete event
    Clear out bucket so CloudFormation can delete it.
    """
    empty_website_bucket(event['ResourceProperties']['BucketName'])

def handler(event, context):
    helper(event, context)
