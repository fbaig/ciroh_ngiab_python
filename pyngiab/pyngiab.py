import logging
import os, glob
import subprocess
import multiprocessing
from pathlib import Path
from packaging.version import Version

class PyNGIAB:
    def __init__(self,
                 data_dir: str,
                 serial_execution_mode: bool = False,
                 venv_path: str = '/ngen/.venv/'):

        # make sure appropriate dependency package versions are available
        self._ngen_env = os.environ.copy()
        if not self._check_dependencies(venv_path):
            raise ModuleNotFoundError(f"Appropriate package versions required for 'ngen' not found. Possible fix is to create virtual environment with appropriate packages and pass virtual environment directory as an argument to initialize 'PyNGIAB' class e.g. `uv venv && uv pip install 'pydantic<2' and numpy={self._ngen_numpy_version}` and then `PyNGIAB(<data_dir>, venv_path=<path_to_venv>)`")

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

    def _check_dependencies(self, venv_path: str) -> bool:
        valid_env = self._validate_dependency_versions(self._ngen_env)
        if not valid_env:
            print(f'Required dependencies not found in system path, looking into {venv_path}')
            if os.path.isdir(venv_path):
                self._ngen_env = {**os.environ, 'PATH': f'{venv_path}/bin:' + os.environ['PATH']}
                valid_env = self._validate_dependency_versions(self._ngen_env)
                if valid_env:
                    print(f'Valid dependencies found in venv: {venv_path}')
                    print('*****************')
                    return True
                pass
        return False

    def _validate_dependency_versions(self, curr_env) -> bool:
        '''
        Subprocess enviornment can differ from python environment. Make sure appropriate
        dependency packages are available to the subprocess environment
        '''
        pydantic_v: Version = self._get_subprocess_python_package_version('pydantic', curr_env)
        numpy_v: Version = self._get_subprocess_python_package_version('numpy', curr_env)

        cmd_str = "/dmod/bin/ngen --info | grep -m 1 -e 'NumPy Version: ' | cut -d ':' -f 2 | uniq | xargs"
        self._ngen_numpy_version = str(subprocess.check_output(cmd_str,
                                                               text=True,
                                                               shell=True)).strip()

        if pydantic_v > Version('1.99') or numpy_v != Version(self._ngen_numpy_version):
            print(f'WARN: pydantic version: Required(v1), Found({pydantic_v}).')
            print(f'WARN: numpy version: Required({self._ngen_numpy_version}), Found({numpy_v}).')
            return False
        return True

    def _get_subprocess_python_package_version(self,
                                               package_name:str,
                                               curr_env) -> Version:
        result:str = subprocess.check_output(['python',
                                              '-c',
                                              f'import {package_name}; print({package_name}.__version__)'],
                                             text=True,
                                             env=curr_env)
        package_v = Version(str(result))
        return package_v

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
                           check=True,
                           env=self._ngen_env)
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
            result = subprocess.run(run_cmd, check=True, env=self._ngen_env)
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
##############################################################
