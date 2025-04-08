FROM pangeo/pangeo-notebook:2024.04.08 AS base

ENV TROUTE_REPO=CIROH-UA/t-route
ENV TROUTE_BRANCH=ngiab
ENV NGEN_REPO=CIROH-UA/ngen
ENV NGEN_BRANCH=ngiab

USER root

###################################
# remove conda/mamba gcc which seems to be broken in pangeo/pangeo-notebook:2024.04.08
# when using with cmake
# Reference: https://github.com/pangeo-data/pangeo-docker-images/issues/604
###################################
# RUN mamba remove --prefix /srv/conda/envs/notebook gcc gcc_linux-64 gcc_impl_linux-64 -y

# Install dependencies
RUN apt-get update && apt-get install -y \
    vim gfortran sqlite3 libsqlite3-dev \
    bzip2 libexpat1-dev libudunits2-dev zlib1g-dev \
    mpich libhdf5-dev libnetcdf-dev libnetcdff-dev libnetcdf-c++4-dev \
    sudo gcc-11 g++-11 make cmake ninja-build tar git gfortran \
    #python3.11 python3.11-dev python3-pip \
    flex bison wget

RUN mamba install -c conda-forge libboost -y
# Make RUN commands use the new environment
SHELL ["mamba", "run", "--no-capture-output", "-n", "notebook", "/bin/bash", "-c"]

###################################
FROM base AS troute_prebuild
WORKDIR /ngen
ENV FC=gfortran NETCDF=/usr/include
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install uv
ADD https://api.github.com/repos/${TROUTE_REPO}/git/refs/heads/${TROUTE_BRANCH} /tmp/version.json
RUN uv pip install --system -r https://raw.githubusercontent.com/$TROUTE_REPO/refs/heads/$TROUTE_BRANCH/requirements.txt
###################################
FROM troute_prebuild AS troute_build
WORKDIR /ngen/t-route
RUN git clone --depth 1 --single-branch --branch $TROUTE_BRANCH https://github.com/$TROUTE_REPO.git .
RUN git submodule update --init --depth 1
RUN uv pip install --system build wheel
RUN sed -i 's/build_[a-z]*=/#&/' compiler.sh
RUN ./compiler.sh no-e
#### TROUTE ####
RUN export CC=/usr/bin/gcc && \
    uv pip install --system --config-setting='--build-option=--use-cython' src/troute-network/
RUN uv build --wheel --config-setting='--build-option=--use-cython' src/troute-network/
RUN export CC=/usr/bin/gcc && \
    uv pip install --system --no-build-isolation --config-setting='--build-option=--use-cython' src/troute-routing/
RUN uv build --wheel --no-build-isolation --config-setting='--build-option=--use-cython' src/troute-routing/
RUN uv build --wheel --no-build-isolation src/troute-config/
RUN uv build --wheel --no-build-isolation src/troute-nwm/
###################################
FROM troute_prebuild AS ngen_clone
WORKDIR /ngen
ADD https://api.github.com/repos/${NGEN_REPO}/git/refs/heads/${NGEN_BRANCH} /tmp/version.json
RUN git clone --single-branch --branch $NGEN_BRANCH https://github.com/$NGEN_REPO.git && \
    cd ngen && \
    git submodule update --init --recursive --depth 1
##################################
FROM ngen_clone AS ngen_build
ENV PATH=/usr/bin:${PATH}:/usr/bin/mpich CC=/usr/bin/gcc
WORKDIR /ngen/ngen

ARG COMMON_BUILD_ARGS="-DNGEN_WITH_EXTERN_ALL=ON \
    -DNGEN_WITH_NETCDF:BOOL=ON \
    -DNGEN_WITH_BMI_C:BOOL=ON \
    -DNGEN_WITH_BMI_FORTRAN:BOOL=ON \
    -DNGEN_WITH_PYTHON:BOOL=ON \
    -DNGEN_WITH_ROUTING:BOOL=ON \
    -DNGEN_WITH_SQLITE:BOOL=ON \
    -DNGEN_WITH_UDUNITS:BOOL=ON \
    -DUDUNITS_QUIET:BOOL=ON \
    -DNGEN_WITH_TESTS:BOOL=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=. \
    -DCMAKE_C_COMPILER=/usr/bin/gcc \
    -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
    "
SHELL ["mamba", "run", "--no-capture-output", "-n", "notebook", "/bin/bash", "-c"]
RUN cmake -G Ninja -B cmake_build_serial -S . ${COMMON_BUILD_ARGS} -DNGEN_WITH_MPI:BOOL=OFF && \
    cmake --build cmake_build_serial --target all -- -j $(nproc)

ARG MPI_BUILD_ARGS="-DNGEN_WITH_MPI:BOOL=ON \
    -DNetCDF_ROOT=/usr/lib/x86_64-linux-gnu \
    -DCMAKE_PREFIX_PATH=/usr/lib/x86_64-linux-gnu"
RUN cmake -G Ninja -B cmake_build_parallel -S . ${COMMON_BUILD_ARGS} ${MPI_BUILD_ARGS} && \
    cmake --build cmake_build_parallel --target all -- -j $(nproc)

##################################
FROM ngen_build AS restructure_files
RUN mkdir -p /dmod/datasets /dmod/datasets/static /dmod/shared_libs /dmod/bin && \
    shopt -s globstar && \
    cp -a ./extern/**/cmake_build/*.so* /dmod/shared_libs/. || true && \
    cp -a ./extern/noah-owp-modular/**/*.TBL /dmod/datasets/static && \
    cp -a ./cmake_build_parallel/ngen /dmod/bin/ngen-parallel || true && \
    cp -a ./cmake_build_serial/ngen /dmod/bin/ngen-serial || true && \
    cp -a ./cmake_build_parallel/partitionGenerator /dmod/bin/partitionGenerator || true && \
    cd /dmod/bin && \
    (stat ngen-parallel && ln -s ngen-parallel ngen) || (stat ngen-serial && ln -s ngen-serial ngen)
###################################
FROM restructure_files AS final

WORKDIR /ngen
COPY --from=ngen_build /ngen /ngen
COPY --from=restructure_files /dmod /dmod

ENV FC=gfortran NETCDF=/usr/include
ENV PATH="/ngen/.venv/bin:$PATH"

RUN ls /dmod/shared_libs

#### TROUTE ####
COPY --from=troute_build /ngen/t-route/src/troute-*/dist/*.whl /tmp/
RUN ln -s /dmod/bin/ngen /usr/local/bin/ngen

# ENV UV_INSTALL_DIR=/root/.cargo/bin
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# ENV PATH="/root/.cargo/bin:${PATH}"

#### TROUTE ####
# RUN uv venv && \
#    uv pip install --system --no-cache-dir /tmp/*.whl netCDF4==1.6.3
RUN uv pip install --system --no-cache-dir /tmp/*.whl netCDF4==1.6.3


RUN rm -rf /tmp/*.whl
RUN echo "/dmod/shared_libs/" >> /etc/ld.so.conf.d/ngen.conf && ldconfig -v
ENV PATH=$PATH:/usr/bin/mpich
RUN uv pip install --system numpy==$(/dmod/bin/ngen --info | grep -e 'NumPy Version: ' | cut -d ':' -f 2 | uniq | xargs)
#ENV PATH="/ngen/.venv/bin:${PATH}"
COPY --from=ngen_clone /ngen/ngen/extern/lstm/lstm /ngen/ngen/extern/lstm
RUN uv pip install --no-cache-dir /ngen/ngen/extern/lstm --extra-index-url https://download.pytorch.org/whl/cpu
# COPY --from=troute_build /tmp/troute_url /ngen/troute_url
# COPY --from=ngen_build /tmp/ngen_url /ngen/ngen_url
RUN echo "export PS1='\u\[\033[01;32m\]@ngiab_dev\[\033[00m\]:\[\033[01;35m\]\W\[\033[00m\]\$ '" >> ~/.bashrc

##################################
# 2i2c template packages
##################################

USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH=${NB_PYTHON_PREFIX}/bin:$PATH

# Needed for apt-key to work
RUN apt-get update -qq --yes > /dev/null && \
    apt-get install --yes -qq gnupg2 > /dev/null && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get -y update \
 && apt-get install -y dbus-x11 \
   firefox \
   xfce4 \
   xfce4-panel \
   xfce4-session \
   xfce4-settings \
   xorg \
   xubuntu-icon-theme \
   curl \
 && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs

# Install TurboVNC (https://github.com/TurboVNC/turbovnc)
ARG TURBOVNC_VERSION=2.2.6
RUN wget -q "https://sourceforge.net/projects/turbovnc/files/${TURBOVNC_VERSION}/turbovnc_${TURBOVNC_VERSION}_amd64.deb/download" -O turbovnc.deb \
    && apt-get update -qq --yes > /dev/null \
    && apt-get install -y ./turbovnc.deb > /dev/null \
    # remove light-locker to prevent screen lock
    && apt-get remove -y light-locker > /dev/null \
    && rm ./turbovnc.deb \
    && ln -s /opt/TurboVNC/bin/* /usr/local/bin/ \
    && rm -rf /var/lib/apt/lists/*

RUN mamba install -n ${CONDA_ENV} -y websockify

# Install jupyter-remote-desktop-proxy with compatible npm version
RUN export PATH=${NB_PYTHON_PREFIX}/bin:${PATH} \
    && npm install -g npm@7.24.0 \
    && uv pip install --system --no-cache-dir \
          https://github.com/jupyterhub/jupyter-remote-desktop-proxy/archive/main.zip

# Install jupyterlab_vim extension and plugin to download the folder/files
RUN uv pip install --system jupyterlab_vim
#RUN uv pip install --system notebook jupyter-tree-download

# Install Google Cloud SDK (gcloud, gsutil)
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && \
    apt-get update -y && \
    apt-get install google-cloud-sdk -y

########################
# Issue installing all packages at the same time
# https://stackoverflow.com/questions/79547588/uv-pip-install-fails-for-multiple-packages
########################
# # Install gis, hydro etc. packages
# RUN uv pip install --system spatialpandas \
#            	   	    easydev \
# 			    colormap \
# 			    colorcet \
# 			    duckdb \
# 			    dask_geopandas \
# 			    hydrotools \
# 			    sidecar \
# 			    dataretrieval \
# 			    google-cloud-bigquery
RUN uv pip install --system spatialpandas
RUN uv pip install --system easydev
RUN uv pip install --system colormap
RUN uv pip install --system colorcet
RUN uv pip install --system duckdb
RUN uv pip install --system dask_geopandas
RUN uv pip install --system hydrotools
RUN uv pip install --system sidecar
RUN uv pip install --system dataretrieval
RUN uv pip install --system google-cloud-bigquery

# Upgrade colorama to resolve dependency conflict
RUN uv pip install --system --upgrade colorama

# Install nb_black separately to address metadata generation issue
RUN uv pip install --system nb_black==1.0.5

# # Install nbfetch for hydroshare
# RUN pip install -U --no-cache-dir --upgrade-strategy only-if-needed git+https://github.com/hydroshare/nbfetch.git@hspuller-auth
# # enable jupyter_server extension
# RUN jupyter server extension enable --py nbfetch --sys-prefix

RUN uv pip install --system dask_labextension

# Update custom Jupyter Lab settings
RUN sed -i 's/\"default\": true/\"default\": false/g' /srv/conda/envs/notebook/share/jupyter/labextensions/@axlair/jupyterlab_vim/schemas/@axlair/jupyterlab_vim/plugin.json

# Downgrade pydantic to avoid issues with ngen is not compatible with pydantic2
RUN uv pip install --system 'pydantic<2'

# To avoid error for ngen-parallel
ENV RDMAV_FORK_SAFE=1

##################################
# ngiab extra stuff
# move before 2i2c packages once tested
##################################

# Setup and install ngiab_data_preprocess module to allow preparing data for ngiab
RUN uv pip install --system ngiab_data_preprocess==4.1.0
RUN uv run python -c "from data_sources.source_validation import download_and_update_hf; download_and_update_hf();"

# Update permissions to make '.ngiab' available to Jupyter non-root user
RUN chown -R ${NB_USER}:${NB_USER} /home/jovyan/.ngiab/

##########
# Teehr (https://github.com/arpita0911patel/ngiab-teehr/tree/main)
##########
WORKDIR /ngen/teehr

RUN apt-get update && apt-get install -y git openjdk-11-jdk

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

RUN git clone https://github.com/arpita0911patel/ngiab-teehr.git

RUN pip install uv
RUN uv pip install --system --no-cache-dir -r ngiab-teehr/requirements.txt

RUN cp -r ngiab-teehr/scripts/* . \
    && rm -r ngiab-teehr

# Update permissions to allow Jupyter non-root user to install packages
RUN chown -R ${NB_USER}:${NB_USER} /home/jovyan/.cache/
# RUN chown -R ${NB_USER}:${NB_USER} /srv/conda/

WORKDIR /ngen/
USER ${NB_USER}