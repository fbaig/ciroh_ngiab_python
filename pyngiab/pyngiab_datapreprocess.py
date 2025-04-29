import os
import subprocess
from enum import Enum
from datetime import datetime

class DataSource(Enum):
    NWM_RETRO_V3 = 'nwm'
    AORC = 'aorc'
    pass

class PyNGIABDataPreprocess:
    def __init__(self,
                 input_feature: str,
                 data_source: DataSource=DataSource.NWM_RETRO_V3):

        self._date_format = '%Y-%m-%d'

        self._cmd = ['python', '-m', 'ngiab_data_cli', '-i', input_feature]

        self._cmd.append('--source')
        self._cmd.append(data_source.value)

        # required for forcings and realization
        self._require_data_range = False
        self._start_date = None
        self._end_date = None

        pass

    def for_latlon(self,
                   latitude: float,
                   longitude: float):
        self._cmd.append('--latlon')
        self._cmd.append(f'{str(latitude)},{str(longitude)}')
        return self

    def for_vpu(self, vpu_id: int):
        self._cmd.append('--vpu')
        self._cmd.append(f'{str(vpu_id)}')
        return self

    def subset(self):
        self._cmd.append('--subset')
        return self

    def generate_forcings(self, start_date: str=None, end_date: str=None):
        self._cmd.append('--forcings')
        self._require_date_range = True
        if self._start_date is None:
            self._start_date = datetime.strptime(start_date, self._date_format)
        if self._end_date is None:
            self._end_date = datetime.strptime(end_date, self._date_format)
        return self

    def generate_realization(self, start_date: str=None, end_date: str=None):
        self._cmd.append('--realization')
        self._require_date_range = True
        if self._start_date is None:
            self._start_date = datetime.strptime(start_date, self._date_format)
        if self._end_date is None:
            self._end_date = datetime.strptime(end_date, self._date_format)
        return self

    def run(self):
        if self._require_date_range and (self._start_date is None or self._end_date is None):
            raise ValueError('Date range need to be specified for either forcings or realization or both')

        self._cmd.append('--start_date')
        self._cmd.append(self._start_date.strftime(self._date_format))

        self._cmd.append('--end_date')
        self._cmd.append(self._end_date.strftime(self._date_format))

        print(f'Running command: {" ".join(self._cmd)}')

        pass

# '''
# Most of the code is copied from the following repository
# Original Author: Josh Cunningham
# Reference: https://github.com/CIROH-UA/NGIAB_data_preprocess/
# '''
# class NGIABDataPreprocess:
#     from data_processing.forcings import create_forcings
#     from data_processing.create_realization import create_realization, create_em_realization
#     from data_processing.datasets import load_aorc_zarr, load_v3_retrospective_zarr
#     from data_processing.dataset_utils import save_and_clip_dataset

#     def __init__(self,
#                  data_dir: str,
#                  serial_execution_mode: bool = False):

#         pass

#     '''

#     '''
#     def subset(input_feature: list[str],
#                latlon: str=None,
#                gage: str=None,
#                ):
#         input_feature = input_feature.replace('_', '-')
#         if len(input_feature.split('-')) > 1:
#         prefix = input_feature.split('-')[0]
#         if prefix.lower() == 'gage':
#             args.gage = True
#         elif prefix.lower() == 'wb':
#             logging.warning('Waterbody IDs are no longer supported!')
#             logging.warning(f'Automatically converting {input_feature} to catid')
#             time.sleep(2)

#         from data_processing.subset import subset
#         subset(feature_to_subset, output_gpkg_path=paths.geopackage_path)
#         pass

#     def subset_vpu():
#         from data_processing.subset import subset_vpu
#         subset_vpu(args.vpu, output_gpkg_path=paths.geopackage_path)
#         logging.info("Subsetting complete.")
#         pass
