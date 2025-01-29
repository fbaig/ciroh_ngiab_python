import subprocess

class NGIAB:
    def __init__(self,
                 data_dir: str,
                 config_file_path: str = '~/.host_data_path.conf',
                 tethys_script_path: str = './viewOnTethys.sh'):

        self._data_dir = data_dir
        self._config_file_path = config_file_path
        self._tethys_script_path = tethys_script_path
        self._image_name = 'awiciroh/ciroh-ngen-image:latest'
        pass

    def _validate_directory(self, directory, name):
        '''Validate the existence of a directory and count its files.'''
        if os.path.isdir(directory):
            count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            print(f"{color}{name}{Colors.Color_Off} exists. {count} {name} files found.")
        else:
            print(f"Error: Directory {directory} does not exist.")

        pass

    def run(self):
        pass
