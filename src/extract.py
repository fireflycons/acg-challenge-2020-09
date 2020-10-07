import csv
import codecs
import requests
from typing import List, Dict
from contextlib import closing


class Extract:
    """
    Extract logic.

    This module handles the acquisition of the datasets.
    It only expects to receive CSV data of some kind
    from the provided sources.

    Given we have explicit filtering rules for this data,
    normally I would filter the JH directly from the input stream
    at read time to save memory, but the conditions of the
    challenge state that filtering must be done in a separate
    transform stage.
    """

    _dataset_urls = None
    _files = None

    def __init__(self, **kwargs):
        """
        Contructor.

        Store the inputs in class attributes.
        We can receive files as well as URLS.
        File data is used by the tests.
        """
        self._dataset_urls = kwargs.get('Urls', None)
        self._files = kwargs.get('Files', None)

    @classmethod
    def from_urls(cls, *dataset_urls):
        """
        Class initializer that sets up to read the data from URLs

        :param urls: List of URLs to read data from
        """
        return cls(Urls=dataset_urls)


    @classmethod
    def from_files(cls, *files):
        """
        Class initializer that sets up to read the data from CSV files

        :param files: List of files to read data from
        """
        return cls(Files=files)


    def _read_csv_from_url(self, url: str) -> List[dict]:
        """
        Reads CSV from given URL

        :param url: URL to pull the data from
        """
        with closing(requests.get(url, stream=True)) as f:
            reader = csv.DictReader(codecs.iterdecode(
                f.iter_lines(), f.encoding), delimiter=",", skipinitialspace=1)
            return list(reader)


    def _read_csv_from_file(self, file_path: str) -> List[dict]:
        """
        Reads CSV from given file

        :param file_path: Path to file to pull the data from
        """
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f, delimiter=",", skipinitialspace=1, strict=1)
            return list(reader)


    def get_datasets(self) -> list:
        """
        Read all CSV datasets passed to one of the class initializers
        """

        if self._dataset_urls:
            return [self._read_csv_from_url(url) for url in self._dataset_urls]
        elif self._files:
            return [self._read_csv_from_file(file_path) for file_path in self._files]
            pass
        else:
            raise RuntimeError("Class not pproperly initialized")

