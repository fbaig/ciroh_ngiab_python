# Python Wrapper for NextGen In A Box (NGIAB)
Python wrapper for [NGIAB](https://github.com/CIROH-UA/NGIAB-CloudInfra/tree/main)'s shell scripts. This will facilitate NGIAB invocation directly from Jupyter environment without the need to execute terminal commands.

This wrapper requires NGIAB already setup so should be tested and run inside NGIAB docker or natively setup NGIAB.

## Getting Started
 - Follow "Quick Start Guide" from [NGIAB](https://github.com/CIROH-UA/NGIAB-CloudInfra/tree/main) to get sample data
 - `docker/docker_run.sh` modifies the [official NGIAB docker](https://github.com/CIROH-UA/NGIAB-CloudInfra/blob/main/docker/Dockerfile) to run NGIAB container with a shell. Modify `/data` mount to point to sample data directory
 - `ngiab.py` has the python wrapper code
 - `test_ngiab.py` has code showing usage of the python wrapper module
    - The same can be done in a Jupyter environment launched with all NGIAB dependencies
```
from ngiab import NGIAB
data_dir = '/data/AWI_16_2863657_007'

# default parallel execution of the model with all available cores
test_ngiab = NGIAB(data_dir)
test_ngiab.run()

# serial execution of the model
test_ngiab_serial = NGIAB(data_dir, serial_execution_mode=True)
test_ngiab_serial.run()
```
## JupyterHub with NGIAB
Most JupyterHub environments are Ubuntu based whereas NGIAB is built on `rockylinux9` as base image. 

### NGIAB with pangeo-notebook as base image (under active development)
[NOTE] `ngiab-ubuntu`, as of now, 
  - builds without `/ngen/troute_url` and `/ngen/ngen_url`

`ngiab-ubuntu/` directory contains dockerfile to generate `ubuntu:22.04` based NGIAB image.

### NGIAB with rockylinux as base image (not under development anymore)
`2i2c_rockylinux/` directory contains `rockylinux9` variant of `2i2c` template image based on popular `pangeo` based dockerfile converted to `rockylinux9` as base image in `pangeo-notebook-rocky/` 