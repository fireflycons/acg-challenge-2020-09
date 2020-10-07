import unittest
import os
import requests
from datetime import date
from src.extract import Extract
from src.transform import Transform, InvalidDatasetError, MissingDatasetError
from constants import Constants

class TransformTests(unittest.TestCase):


    def test_transform_raises_MissingDatSetError_when_no_datasets_given(self):
        """
        When the transformer class receives no data, exception should be raised
        """
        transformer = Transform([])
        self.assertRaises(MissingDatasetError, transformer.transform_data)


    def test_transform_raises_MissingDatSetError_when_one_dataset_given(self):
        """
        When the transformer class receives only one dataset, exception should be raised
        """
        transformer = Transform(Extract.from_files(Constants._NYT_DATA_GOOD).get_datasets())
        self.assertRaises(MissingDatasetError, transformer.transform_data)


    def test_transform_raises_InvalidDatasetError_when_column_is_missing(self):
        """
        If a requied column is missing from a dataset, exception should be raised
        """
        transformer = Transform(Extract.from_files(Constants._NYT_DATA_MISSING_COLUMN).get_datasets())
        self.assertRaises(InvalidDatasetError, transformer.transform_data)


    def test_transform_raises_InvalidDatasetError_when_dataset_does_not_contain_dict_records(self):
        """
        if dataset is not dict records, exception should be raised
        """
        transformer = Transform(['string record',])
        self.assertRaises(InvalidDatasetError, transformer.transform_data)


    def test_transform_raises_InvalidDatasetError_when_date_cannot_be_parsed(self):
        """
        if a date cannot be parsed, exception should be raised
        """
        transformer = Transform(Extract.from_files(Constants._NYT_DATA_BAD_DATE, Constants._JH_DATA_GOOD).get_datasets())
        self.assertRaises(InvalidDatasetError, transformer.transform_data)


    def test_transform_with_valid_data_returns_correct_date_range(self):
        """
        When two valid dataasets are input, the merged output should only
        have rows for the dates in common across both inputs

        JH input ranges from 2020-01-22 to 2020-02-03
        NYT input ranges from 2020-01-21 to 2020-02-03
        Valid range therefore 2020-01-22 to 2020-02-03
        """
        expected_min_date = date(2020, 1, 22)
        expected_max_date = date(2020, 2, 3)

        transformer = Transform(Extract.from_files(Constants._NYT_DATA_GOOD, Constants._JH_DATA_GOOD).get_datasets())
        merged_data = transformer.transform_data()
        min_date = min([d['date'] for d in merged_data])
        max_date = max([d['date'] for d in merged_data])

        assert min_date == expected_min_date and max_date == expected_max_date
