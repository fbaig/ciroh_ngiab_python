# Python Wrapper for NextGen In A Box (NGIAB) in Jupyter
Python wrapper for [NGIAB](https://github.com/CIROH-UA/NGIAB-CloudInfra/tree/main)'s shell scripts. This will facilitate NGIAB invocation directly from Jupyter environment without the need to execute terminal commands.

This wrapper requires NGIAB already setup so should be tested and run inside NGIAB docker or natively setup NGIAB.

Most JupyterHub environments are Ubuntu based whereas NGIAB is built on `rockylinux9` as base image. The repository also contains scripts to create modified versions of NGIAB compatible with Jupyter based on `pangeo/pangeo-notebook` image.

## Getting Started

### Sample Data
 - Follow "Quick Start Guide" from [NGIAB](https://github.com/CIROH-UA/NGIAB-CloudInfra/tree/main) to get sample data

### Generate Data Using [`ngiab_data_preprocess`](https://github.com/CIROH-UA/NGIAB_data_preprocess/tree/main) utility
The utility is part of the docker image and can be executed to download and generate input data for the NGIAB model.

```bash
python -m ngiab_data_cli -i cat-5173 -a --start 2022-01-01 --end 2022-02-28
```
For further ways to run the utility, please refer to [NBIAB Data Preprocess documentation](https://github.com/CIROH-UA/NGIAB_data_preprocess/tree/main?tab=readme-ov-file#examples).

### Running Jupyter with NGIAB
 - A compiled image is available at [https://quay.io/repository/fbaig25/ngiab-2i2c](https://quay.io/repository/fbaig25/ngiab-2i2c) 
 - The same image can be used to launch [2i2c staging JupyterHub](https://staging.ciroh.awi.2i2c.cloud) with custom image
 - Local Jupyter environment with `ngen` can be launched using following
    - Make sure to mount appropriate data directory 
```
docker run -it \
       -v "${PWD}":/shared/ \
       -p 8888:8888 \
       quay.io/fbaig25/ngiab-2i2c:latest \
       jupyter lab --ip 0.0.0.0 /shared
```

### NGIAB Pyhton Wrapper
 - `ngiab.py` has the python wrapper code with can imported as a python module
 - `test_ngiab.py` has code showing usage of the python wrapper module
    - The same can be done in a Jupyter environment launched with all NGIAB dependencies
```python
from ngiab import NGIAB
data_dir = './AWI_16_2863657_007'

# default parallel execution of the model with all available cores
test_ngiab = NGIAB(data_dir)
test_ngiab.run()

# serial execution of the model
test_ngiab_serial = NGIAB(data_dir, serial_execution_mode=True)
test_ngiab_serial.run()
```

## Compiling From Source
 - `ngiab-pangeo/` directory contains scripts to generate `pangeo/pangeo-notebook:2024.04.08` based NGIAB image. The image also adheres to [template](https://github.com/CIROH-UA/awi-ciroh-image/tree/main) required for 2i2c JupyterHub environment provided by CIROH.
    - `docker_run.sh` build a local image with `Jupyter`, `ngen` and `2i2c` packages.
    - Once built successfully, the script also launches a container for local working.
	- [!WARNING] `ngiab-pangeo`, as of now, builds without `/ngen/troute_url` and `/ngen/ngen_url`