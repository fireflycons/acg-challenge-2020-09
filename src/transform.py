import csv
import codecs
from itertools import zip_longest
from datetime import datetime, date
from typing import List, Dict

class InvalidDatasetError(Exception):
    """
    Raised when there is an issue with the format of a dataset
    """
    def __init__(self, reason):
        self.message = f'Invalid format for dataset: {reason}'


class MissingDatasetError(Exception):
    """
    Raised when one of both of the required datasets could not be identified
    """
    def __init__(self, dataset_names: list):
        self.dataset_names = dataset_names
        self.message = f'Datasets were not received for {", ".join(dataset_names)}'


class Transform:
    """
    Handles all data transformation logic
    """

    # Required fields for each dataset
    _JOHN_HOPKINS_FIEILDS = ('Date', 'Country/Region', 'Province/State', 'Lat', 'Long', 'Confirmed', 'Recovered', 'Deaths')
    _NYT_FIELDS = ('date', 'cases', 'deaths')

    def __init__(self, datasets: list):
        """
        Constructor.
        Store a list of datasets to transform.
        At this stage we do not know/care what the data represents.
        """
        self._datasets = datasets
        self._identified_datasets = {
            'NYT': None,
            'JohnHopkins': None
        }

    def _datum_has_fields(self, datum: dict, fields: tuple) -> bool:
        """
        Test whether given dict contains all given fields
        """
        return all(f in datum.keys() for f in fields)


    def _is_nyt_data(self, datum: dict) -> bool:
        """
        Test whether given dict contains all expected NYT fields
        """
        return self._datum_has_fields(datum, self._NYT_FIELDS)


    def _is_jh_data(self, datum: dict) -> bool:
        """
        Test whether given dict contains all expected John Hopkins fields
        """
        return self._datum_has_fields(datum, self._JOHN_HOPKINS_FIEILDS)


    def _identify_datasets(self):
        """
        From the list of datasets passed to the constructor, identify which is which.
        Raise various exceptions if the format of the data is incorrect

        :returns: self (for method chaining)
        """
        for dataset in [ds for ds in self._datasets if ds]:
            if isinstance(dataset, list):
                datum = dataset[0]
                if not isinstance(datum, dict):
                    raise InvalidDatasetError('Cannot find a dict record')
                if self._is_nyt_data(datum):
                    self._identified_datasets['NYT'] = dataset
                elif self._is_jh_data(datum):
                    self._identified_datasets['JohnHopkins'] = dataset
                else:
                    raise InvalidDatasetError('Required columns are missing')
            else:
                raise InvalidDatasetError(f'Expected dataset to be a list, but found {type(dataset)}')
        else:
            # Check we received both
            missing_data = [key for key in self._identified_datasets.keys() if not self._identified_datasets[key]]
            if missing_data:
                raise MissingDatasetError(missing_data)

        return self


    def _transform_johnhopkins(self):
        """
        Transform JH data to required fields, filtering on US data and converting dates to date objects

        :returns: self (for method chaining)
        """
        try:
            self._identified_datasets['JohnHopkins']  = list(
                map(lambda r: {
                    'date': datetime.strptime(r['Date'], '%Y-%m-%d').date(),
                    'recovered': int(r['Recovered'])
                },
                    filter(lambda r: r['Country/Region'] == 'US', self._identified_datasets['JohnHopkins'])
                ))
        except ValueError as e:
            raise InvalidDatasetError(f'{e}')

        return self


    def _transform_nyt(self):
        """
        Transform NYT data to required fields, converting dates to date objects

        :returns: self (for method chaining)
        """
        try:
            self._identified_datasets['NYT'] = list(
                map(lambda r: {
                    'date': datetime.strptime(r['date'], '%Y-%m-%d').date(),
                    'cases': int(r['cases']),
                    'deaths': int(r['deaths'])
                },
                    self._identified_datasets['NYT']
                ))
        except ValueError as e:
            raise InvalidDatasetError(f'{e}')

        return self


    def _merge_datasets(self) -> List[dict]:
        """
        Merge the two datasets keyed on date property, dropping rows
        from either without matching keys

        :returns: merged dataset
        """
        # Get set of dates in common to both datasets
        dates_in_common = set([datum['date'] for datum in self._identified_datasets['JohnHopkins']]) & set([datum['date'] for datum in self._identified_datasets['NYT']])

        # Trim both inputs to only those rows that have the same dates
        dataset1 = [datum for datum in self._identified_datasets['JohnHopkins'] if datum['date'] in dates_in_common]
        dataset2 = [datum for datum in self._identified_datasets['NYT'] if datum['date'] in dates_in_common]

        # Merge data and return
        return [{**u, **v} for u, v in zip_longest(dataset1, dataset2, fillvalue={})]


    def transform_data(self):
        """
        Perform the entire data trasformation and return the merged data

        :returns: merged dataset
        """

        return self._identify_datasets()._transform_johnhopkins()._transform_nyt()._merge_datasets()
