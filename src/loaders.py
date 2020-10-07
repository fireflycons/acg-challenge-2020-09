import boto3
import gviz_api

from datetime import datetime, date
from boto3.dynamodb.conditions import Key
from typing import List, Dict

class GVizCollector:
    """
    Builds a Google Visualization datatable from the dataset
    """
    _column_definitions = {
        'date': ('date', 'Date'),
        'cases': ('number', 'Cases'),
        'deaths': ('number', 'Deaths'),
        'recovered': ('number', 'Recovered')
    }
    _dataset = []


    def __init__(self, bucket_name, key):
        self._bucket_name = bucket_name
        self._key = key


    def add_rows(self, rows: any) -> None:
        if not rows:
            return
        if isinstance(rows, dict):
            self._dataset.append(rows)
        elif isinstance(rows, list):
            self._dataset.extend(rows)
        else:
            raise ValueError(f'Cannot add value of type {type(rows)} to gviz dataset.')


    def write_to_s3(self) -> None:
        datatable = gviz_api.DataTable(self._column_definitions)
        datatable.LoadData(self._dataset)
        json_data = datatable.ToJSon(columns_order=('date', 'cases', 'deaths', 'recovered'),
                                     order_by='date')
        code = f'function createDataset() {{ return {{ getDataTable: function () {{ return new google.visualization.DataTable({json_data}); }} }}; }}'
        boto3.resource('s3').Bucket(self._bucket_name).put_object(
            Key=self._key,
            Body=code.encode('utf-8')
        )


class DynamoDBLoader:
    """
    Handles load logic for a DynamoDB repository

    If we were being clever, we could have an abstract base class Loader
    and derive this and other repo targets, e.g. RDS
    """

    # We'll use this as the partition key so that date can be a sort key for queries.
    # There could conceivably be other countries datasets.
    _US_DATASET = 1

    # Maximum number of records that can be written to dynamo in batches
    _MAX_BATCH_SIZE = 25

    def __init__(self, table_name: str, dataset: list, collector: GVizCollector):
        """
        Constructor.

        Store DynamoDB table name and dataset to load
        Create a boto resource for the DDB connection
        """
        self._table_name = table_name
        self._dataset  = dataset
        self._dynamodb = boto3.resource('dynamodb')
        self._collector = collector

    def _render_dynamo_item(self, record: dict) -> dict:
        """
        Render a single record for database insertion, adding partition key and converting date to string

        :param record: Record to render
        :return: Record suitable for insertion to dynamo
        """
        return {
            'dataset': self._US_DATASET,
            'date': record['date'].__str__(),
            'cases': record['cases'],
            'deaths': record['deaths'],
            'recovered': record['recovered']
        }


    def _batch_insert_repository(self, records_to_write: List[dict]) -> None:
        """
        Push a batch of records to the repository.
        This will take a little time on initial load since WCU is low

        :param records_to_write: Records that need inseting in the database
        """
        def batch_records(dataset: List[dict]) -> List[dict]:
            """
            Generator that yields batches of records for BatchWriteItem
            """
            for i in range(0, len(dataset), self._MAX_BATCH_SIZE):
                yield dataset[i:i + self._MAX_BATCH_SIZE]

        for batch in batch_records(records_to_write):
            self._dynamodb.batch_write_item(RequestItems={
                self._table_name:  [
                        {
                            'PutRequest': {
                                'Item': self._render_dynamo_item(record)
                            }
                        }
                    for record in batch
                    ]
                }
            )


    def read_all_data(self) -> List[dict]:
        """
        Read the entire dataset from Dynamo
        This is inexpensive because the dataset is small
        and we only do it once a day.
        """
        table = self._dynamodb.Table(self._table_name)

        start_key = None
        dataset = []

        while True:
            # Loop until the query retrieves all the data
            if start_key:
                response = table.query(
                    Select='ALL_ATTRIBUTES',
                    ConsistentRead=False,
                    ScanIndexForward=True,
                    KeyConditionExpression=Key('dataset').eq(1),
                    ExclusiveStartKey=start_key
                )
            else:
                response = table.query(
                    Select='ALL_ATTRIBUTES',
                    ConsistentRead=False,
                    ScanIndexForward=True,
                    KeyConditionExpression=Key('dataset').eq(1),
                )

            dataset.extend([
                {
                    'date': datetime.strptime(item['date'], '%Y-%m-%d').date(),
                    'cases': int(item['cases']),
                    'deaths': int(item['deaths']),
                    'recovered': int(item['recovered'])
                }
                for item in response['Items']
            ])

            start_key = response.get('LastEvaluatedKey', None)

            if not start_key:
                break

        return dataset


    def update_repository(self) -> None:
        """
        Update repository with latest data
        """

        # Get all the data so far
        # This will be sorted in ascending SORT KEY order, i.e. date
        existing_data = self.read_all_data()

        # Add to gviz data
        self._collector.add_rows(existing_data)

        # Aggegate on most recent date
        last_entry_date = existing_data[-1]['date'] if existing_data else date.min

        # Filter dataset for records newer than last entry
        records_to_write = list(filter(lambda r: r['date'] > last_entry_date, self._dataset))
        record_count = len(records_to_write)

        # Add new rows to gviz data
        self._collector.add_rows(records_to_write)

        if record_count == 0:
            # Nothing to do
            return record_count

        if record_count > 1:
            # More than one, then batch
            self._batch_insert_repository(records_to_write)
            return record_count

        # If we get here, then single record
        self._dynamodb.Table(self._table_name).put_item(
            Item=self._render_dynamo_item(records_to_write[0])
        )

        return record_count

