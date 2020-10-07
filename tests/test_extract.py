import unittest
import os
from src.extract import Extract
from constants import Constants

class ExtractTests(unittest.TestCase):


    def test_extract_from_two_files_returns_two_datasets(self):
        """
        Test we can load files. Will be used in other tests
        """

        extractor = Extract.from_files(Constants._JH_DATA_GOOD, Constants._NYT_DATA_GOOD)
        datasets = extractor.get_datasets()
        assert len(datasets) == 2


    def test_extract_from_two_urls_returns_two_datasets(self):
        """
        Test we can load URLs
        """
        extractor = Extract.from_urls(Constants._JH_URL, Constants._NYT_URL)
        datasets = extractor.get_datasets()
        assert len(datasets) == 2
