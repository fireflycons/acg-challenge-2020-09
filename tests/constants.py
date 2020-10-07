import os


class Constants:

    _TEST_DIRECTORY = os.path.dirname(__file__)
    _JH_DATA_GOOD = os.path.join(_TEST_DIRECTORY, 'jh_data_good.csv')
    _NYT_DATA_GOOD = os.path.join(_TEST_DIRECTORY, 'nyt_data_good.csv')
    _NYT_DATA_MISSING_COLUMN = os.path.join(
        _TEST_DIRECTORY, 'nyt_data_missing_column.csv')
    _NYT_DATA_BAD_DATE = os.path.join(
        _TEST_DIRECTORY, 'nyt_data_bad_date_value.csv')
    _JH_URL = 'https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv?opt_id=oeu1598165794642r0.7137185818243232'
    _NYT_URL = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv'

    _DDB_STREAM_EVENT = {
        "Records": [
            {
                "eventID": "69c93f413aed6c7c4e1d5b1562862a14",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-west-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1601212164.0,
                    "Keys": {
                        "date": {
                            "S": "2020-07-15"
                        },
                        "dataset": {
                            "N": "1"
                        }
                    },
                    "NewImage": {
                        "date": {
                            "S": "2020-07-15"
                        },
                        "recovered": {
                            "N": "1075882"
                        },
                        "cases": {
                            "N": "3513667"
                        },
                        "dataset": {
                            "N": "1"
                        },
                        "deaths": {
                            "N": "137326"
                        }
                    },
                    "SequenceNumber": "17600000000024804288945",
                    "SizeBytes": 86,
                    "StreamViewType": "NEW_IMAGE"
                },
                "eventSourceARN": "arn:aws:dynamodb:eu-west-1:123456789012:table/acg-challenge-CovidDataTable-JDOUDWJJCRXK/stream/2020-09-27T12:57:28.175"
            },
            {
                "eventID": "f4bf8113a094b3b8eb78a0bb84e72f20",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-west-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1601212164.0,
                    "Keys": {
                        "date": {
                            "S": "2020-07-16"
                        },
                        "dataset": {
                            "N": "1"
                        }
                    },
                    "NewImage": {
                        "date": {
                            "S": "2020-07-16"
                        },
                        "recovered": {
                            "N": "1090645"
                        },
                        "cases": {
                            "N": "3589349"
                        },
                        "dataset": {
                            "N": "1"
                        },
                        "deaths": {
                            "N": "138284"
                        }
                    },
                    "SequenceNumber": "17700000000024804288946",
                    "SizeBytes": 86,
                    "StreamViewType": "NEW_IMAGE"
                },
                "eventSourceARN": "arn:aws:dynamodb:eu-west-1:123456789012:table/acg-challenge-CovidDataTable-JDOUDWJJCRXK/stream/2020-09-27T12:57:28.175"
            }
        ]
    }

    _DDB_STREAM_DELETE_EVENT = {
        "Records": [
            {
                "eventID": "0d615e77959bf4ffb5bc699cf5972752",
                "eventName": "REMOVE",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "eu-west-1",
                "dynamodb": {
                    "ApproximateCreationDateTime": 1601217365.0,
                    "Keys": {
                        "date": {
                            "S": "2020-01-22"
                        },
                        "dataset": {
                            "N": "1"
                        }
                    },
                    "SequenceNumber": "24900000000024807323778",
                    "SizeBytes": 23,
                    "StreamViewType": "NEW_IMAGE"
                },
                "eventSourceARN": "arn:aws:dynamodb:eu-west-1:104552851521:table/acg-challenge-CovidDataTable-JDOUDWJJCRXK/stream/2020-09-27T12:57:28.175"
            }
        ]
    }
