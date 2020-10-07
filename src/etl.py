# https://acloudguru.com/blog/engineering/cloudguruchallenge-python-aws-etl#

import os
import json
import boto3
from extract import Extract
from transform import Transform, InvalidDatasetError, MissingDatasetError
from loaders import DynamoDBLoader, GVizCollector

def do_etl(dynamo_table, website_bucket, url1, url2):
    """
    Performs the ETL
    """
    gviz_collector = GVizCollector(website_bucket, 'dataset.js')
    record_count = DynamoDBLoader(dynamo_table,
                        Transform(
                            Extract.from_urls(url1, url2).get_datasets()
                        ).transform_data(),
                        gviz_collector
                ).update_repository()

    print(f'{record_count} new records stored')
    gviz_collector.write_to_s3()
    print('BI dataset written to S3')


def handler(_, __):
    """
    Lambda entry point
    """
    try:
        # Perform ETL
        do_etl(
            os.environ['TABLE'],
            os.environ['WEBSITE_BUCKET'],
            os.environ['JH_DATA_URL'],
            os.environ['NYT_DATA_URL']
        )
    except Exception as e:
        exception_type = e.__class__.__name__
        exception_message = e.message if hasattr(e, 'message') else str(e)

        # Log to CW
        print(f'EXCEPTION ({exception_type}): {exception_message}')

        machine_readable_message = {
            'Source': 'Covid ETL',
            'ExceptionType': exception_type,
            'Message': exception_message,
            'Arguments': e.args
        }

        email_message = '\n'.join(
            (
                'An exception was caught in the Covid ETL job',
                f'Exception Type: {exception_type}',
                f'Message: {exception_message}'
                f'Arguments: {",".join(e.args)}'
            )
        )

        sns_payload = {
            'default': f'301 Redirect Exception: {exception_message}',
            'email': email_message,
            'lambda': json.dumps(machine_readable_message),
            'sqs': json.dumps(machine_readable_message)
        }

        try:
            boto3.client('sns').publish(
                TopicArn=os.environ['ERROR_TOPIC_ARN'],
                Subject='Exception in Covid ETL job',
                MessageStructure='json',
                Message=json.dumps(sns_payload)
            )

        except Exception as inner:
            print(f'PANIC: Unable to report exception to SNS due to {inner}')

        # Re-raise to mark the lambda as failed
        raise
