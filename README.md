# PyNGIAB

**Stable JupyterHub Compatible NGIAB:** https://github.com/CIROH-UA/awi-ciroh-image/tree/ngen-2i2c 

[!Note] This repository should be treated as having the latest (possibly buggy/nightly build) versions of the two main components of PyNGIAB.

---

PyNGIAB is designed to allow execution of an end-to-end hydrologic modeling workflow using the [Nextgen framework](https://github.com/NOAA-OWP/ngen) in Python from a Jupyter environment. To this end, there are two major components of PyNGIAB

1. JupyterHub (e.g. 2i2c) compatible NGIAB.

Most JupyterHub environments are Ubuntu based whereas [NGIAB](https://github.com/CIROH-UA/NGIAB-CloudInfra) is built on `rockylinux9` as base image. This repository contains scripts to create modified versions of NGIAB compatible with Jupyter based on `pangeo/pangeo-notebook` image.

2. Python wrapper libraries for NGIAB.

Python wrappers for [data preprocessing](https://github.com/CIROH-UA/NGIAB_data_preprocess) and [NGIAB](https://github.com/CIROH-UA/NGIAB-CloudInfra)'s model execution shell scripts. This facilitates NGIAB invocation directly from Jupyter environment without the need to execute terminal commands.


## JupyterHub (e.g. 2i2c) compatible NGIAB
The JupyterHub environment with pre-configured NGIAB can be accessed via 

- [CIROH 2i2c JupyterHub Production](http://staging.ciroh.awi.2i2c.cloud/)
- [CIROH 2i2c JupyterHub Staging/Dev](http://staging.ciroh.awi.2i2c.cloud/)
- Run Local JupyterHub
  - A compiled image is available at [https://quay.io/repository/fbaig25/ngiab-2i2c](https://quay.io/repository/fbaig25/ngiab-2i2c). Alternatively, you can use following to build local image
    - `Dockerfile:` Creates `pangeo/pangeo-notebook:2024.04.08` based NGIAB image. The image also adheres to [template](https://github.com/CIROH-UA/awi-ciroh-image/tree/main) required for 2i2c JupyterHub environment provided by CIROH.
    - `docker_run.sh`: Builds a local image with `Jupyter`, `ngen` and `2i2c` packages.
    - Once built successfully, Jupyter interface can usually be accessed at `http://127.0.0.1:8888/`
  - Local Jupyter environment with `ngen` can be launched using following (Make sure to mount appropriate data directory) 
```
docker run -it \
       -v "${PWD}":/shared/ \
       -p 8888:8888 \
       quay.io/fbaig25/ngiab-2i2c:latest \
       jupyter lab --ip 0.0.0.0 /shared
```
- [Upcoming] [The I-GUIDE Platform JupyterHub](https://jupyter.iguide.illinois.edu/)


## Python wrapper libraries

If not available, `PyNGIAB` module can be installed via 
```bash
pip install git+https://github.com/fbaig/ciroh_pyngiab.git
```

### (1) Data Pre-processing
Above container images come installed with [`ngiab_data_preprocess`](https://github.com/CIROH-UA/NGIAB_data_preprocess/tree/main) utility which can be used to (1) subset data, (2) generate forcings and (3) generate realization. These are used as input to execute the Nextgen model framework.

```bash
python -m ngiab_data_cli -i cat-5173 -a --start 2022-01-01 --end 2022-02-28
```
For further details about the use of the utility, please refer to [NBIAB Data Preprocess documentation](https://github.com/CIROH-UA/NGIAB_data_preprocess/tree/main?tab=readme-ov-file#examples).

#### Sample Data
 - Sample data is available in `/tests/` directory in the container image
 - Alternatively, you can also follow "Quick Start Guide" from [NGIAB](https://github.com/CIROH-UA/NGIAB-CloudInfra/tree/main) to manually download sample data




### (2) Model Execution
- `pyngiab/` has the python code files for `PyNGAIB` modules
- `tests/` has unit tests and common CI/CD workflows for automated testing
- `test_ngiab.py` has code showing usage of the python wrapper module

```python
from pyngiab import PyNGIAB

data_dir = './AWI_16_2863657_007'

# default parallel execution of the model with all available cores
test_ngiab = PyNGIAB(data_dir)
test_ngiab.run()

# serial execution of the model
test_ngiab_serial = PyNGIAB(data_dir, serial_execution_mode=True)
test_ngiab_serial.run()
```