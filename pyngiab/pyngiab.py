import logging
import os, glob
import subprocess
import multiprocessing
from pathlib import Path

class PyNGIAB:
    def __init__(self,
                 data_dir: str,
                 serial_execution_mode: bool = False):

        self._data_dir = data_dir
        self._serial_execution_mode = serial_execution_mode

        self._cpu_count = multiprocessing.cpu_count()

        '''
        Note: Only first file is used.
        Since ngen runs from the data directory itself, remove preceeding path
        '''
        self._selected_catchment = [p.relative_to(self._data_dir) for p in list(Path(self._data_dir).rglob('*.gpkg'))]
        self._selected_nexus = [p.relative_to(self._data_dir) for p in list(Path(self._data_dir).rglob('*.gpkg'))]
        self._selected_realizations = [p.relative_to(self._data_dir) for p in list(Path(self._data_dir).rglob('*realization*.json'))]

        self._partitions_file = list(Path(self._data_dir).rglob(f'*partitions_{self._cpu_count}.json'))

        pass

    def _validate_directory(self, directory, name) -> bool:
        '''Validate the existence of a directory and count its files.'''
        if os.path.isdir(directory):
            count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            print(f'{name} exists. {count} {name} files found.')
            return True
        else:
            print(f'Error: Directory {directory} does not exist.')
            return False
        pass

    def _validate_inputs(self) -> bool:
        # Validate required subdirectories in data_dir path
        if (not self._validate_directory(os.path.join(self._data_dir, 'forcings'),'forcings') or
            not self._validate_directory(os.path.join(self._data_dir,'config'), 'config') or
            not self._validate_directory(os.path.join(self._data_dir, 'outputs'), 'outputs')):
            return False

        # Validate required catchment, nexus and realization files
        if len(self._selected_catchment) <= 0:
            print(f'No catchment files found')
            return False
        elif len(self._selected_nexus) <= 0:
            print(f'No nexus files found')
            return False
        elif len(self._selected_realizations) <= 0:
            print(f'No realization files found')
            return False

        return True

    def _generate_partition(self,
                            catchment_data_path: str,
                            nexus_data_path: str
                            ) -> str:
        partitions_output_path: str = f'partitions_{self._cpu_count}.json'
        try:
            subprocess.run(['/dmod/bin/partitionGenerator',
                            catchment_data_path,
                            nexus_data_path,
                            partitions_output_path,
                            str(self._cpu_count),
                            '',
                            ''
                            ],
                           check=True)
            return partitions_output_path
        except subprocess.CalledProcessError as e:
            print(f'NBIAB partitioning failed with status {e.returncode}.')
        return None

    def run(self) -> bool:
        if not self._validate_inputs(): return

        ''' NextGen model utility expect to run in data directory '''
        cwd = os.getcwd()
        os.chdir(self._data_dir)

        try:
            run_cmd = []
            if (self._serial_execution_mode):
                print('Run NextGen Model Framework in Serial Model ...')
                run_cmd = ['/dmod/bin/ngen-serial',
                           self._selected_catchment[0],
                           'all',
                           self._selected_nexus[0],
                           'all',
                           self._selected_realizations[0]
                           ]
                print('Running command: ' + ' '.join(str(x) for x in run_cmd))
            else:
                print('Run NextGen Model Framework in Parallel Model ...')
                # generate partitions if required
                if (len(self._partitions_file) <= 0):
                    print('No partitions file found, generating ...')
                    self._partitions_file = self._generate_partition(self._selected_catchment[0],
                                                                     self._selected_nexus[0])
                    print('Partitions file generated: ' + os.path.abspath(self._partitions_file))
                    pass
                else:
                    self._partitions_file = self._partitions_file[0]
                    pass
                # model command in parallel mode
                run_cmd = ['mpirun',
                           '-n',
                           str(self._cpu_count),
                           '/dmod/bin/ngen-parallel',
                           self._selected_catchment[0],
                           'all',
                           self._selected_nexus[0],
                           'all',
                           self._selected_realizations[0],
                           self._partitions_file
                           ]
                pass

            # execute NGIAB model
            result = subprocess.run(run_cmd, check=True)
            print('NGIAB executed successfully ...')
            return True
        except Exception as e:
            print(f'NGIAB failed to run: {e}')
            return False
        finally:
            # change directory back to working directory
            os.chdir(cwd)
        return False
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
