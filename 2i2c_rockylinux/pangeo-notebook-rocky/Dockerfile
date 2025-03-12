FROM rockylinux:9.1
# build file for pangeo images

#LABEL org.opencontainers.image.source=https://github.com/pangeo-data/pangeo-docker-images

# Setup environment variables
ENV CONDA_ENV=notebook \
    NB_USER=jovyan \
    NB_UID=1000 \
    SHELL=/bin/bash \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    CONDA_DIR=/srv/conda

ENV NB_PYTHON_PREFIX=${CONDA_DIR}/envs/${CONDA_ENV} \
    HOME=/home/${NB_USER}

ENV PATH=${NB_PYTHON_PREFIX}/bin:${CONDA_DIR}/bin:${PATH}
ENV DASK_ROOT_CONFIG=${CONDA_DIR}/etc

RUN echo "Creating ${NB_USER} user..." \
    && groupadd --gid ${NB_UID} ${NB_USER}  \
    && useradd --create-home --gid ${NB_UID} --no-log-init --uid ${NB_UID} ${NB_USER} \
    && chown -R ${NB_USER}:${NB_USER} /srv

RUN echo ". ${CONDA_DIR}/etc/profile.d/conda.sh ; conda activate ${CONDA_ENV}" > /etc/profile.d/init_conda.sh

# Install required packages
RUN dnf install -y epel-release \
    && dnf install -y wget zip tzdata bzip2 git \
    && dnf clean all

ENV TZ=UTC

USER ${NB_USER}
WORKDIR ${HOME}

# Install latest mambaforge in ${CONDA_DIR}
RUN echo "Installing Miniforge..." \
    && URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh" \
    && wget --quiet ${URL} -O installer.sh \
    && /bin/bash installer.sh -u -b -p ${CONDA_DIR} \
    && rm installer.sh \
    && ${CONDA_DIR}/bin/mamba install conda-lock -y \
    && ${CONDA_DIR}/bin/mamba clean -afy \
    && find ${CONDA_DIR} -follow -type f -name '*.a' -delete

USER root
COPY --chown=jovyan:jovyan . /home/jovyan

RUN echo "Checking for 'binder' or '.binder' subfolder" \
        ; if [ -d binder ] ; then echo "Using 'binder/' build context" \
        ; elif [ -d .binder ] ; then echo "Using '.binder/' build context" \
        ; else echo "Using './' build context" ; fi

RUN echo "Checking for 'apt.txt'..." \
        ; [ -d binder ] && cd binder \
        ; [ -d .binder ] && cd .binder \
        ; if test -f "apt.txt" ; then \
        dnf install -y $(cat apt.txt) \
        && dnf clean all \
        ; fi

RUN echo "Checking for 'jupyter_notebook_config.py'..." \
        ; [ -d binder ] && cd binder \
        ; [ -d .binder ] && cd .binder \
        ; if test -f "jupyter_notebook_config.py" ; then \
        mkdir -p /etc/jupyter \
        && cp jupyter_notebook_config.py /etc/jupyter \
        ; fi

USER ${NB_USER}

RUN echo "Checking for 'conda-lock.yml' or 'environment.yml'..." \
        ; [ -d binder ] && cd binder \
        ; [ -d .binder ] && cd .binder \
        ; if test -f "conda-lock.yml" ; then echo "Using conda-lock.yml" & \
        conda-lock install --name ${CONDA_ENV} \
        ; elif test -f "environment.yml" ; then echo "Using environment.yml" & \
        ${CONDA_DIR}/bin/mamba env create --name ${CONDA_ENV} -f environment.yml  \
        ; else echo "No conda-lock.yml or environment.yml! *creating default env*" ; \
        ${CONDA_DIR}/bin/mamba create --name ${CONDA_ENV} pangeo-notebook \
        ; fi \
        && ${CONDA_DIR}/bin/mamba clean -yaf \
        && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
        && find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete \
        ; if ls ${NB_PYTHON_PREFIX}/lib/python*/site-packages/bokeh/server/static > /dev/null 2>&1; then \
        find ${NB_PYTHON_PREFIX}/lib/python*/site-packages/bokeh/server/static -follow -type f -name '*.js' ! -name '*.min.js' -delete \
        ; fi

RUN echo "Checking for pip 'requirements.txt'..." \
        ; [ -d binder ] && cd binder \
        ; [ -d .binder ] && cd .binder \
        ; if test -f "requirements.txt" ; then \
        ${NB_PYTHON_PREFIX}/bin/pip install --no-cache -r requirements.txt \
        ; fi

RUN echo "Checking for 'postBuild'..." \
        ; [ -d binder ] && cd binder \
        ; [ -d .binder ] && cd .binder \
        ; if test -f "postBuild" ; then \
        chmod +x postBuild \
        && ./postBuild \
        && rm -rf /tmp/* \
        && rm -rf ${HOME}/.cache ${HOME}/.npm ${HOME}/.yarn \
        && rm -rf ${NB_PYTHON_PREFIX}/share/jupyter/lab/staging \
        && find ${CONDA_DIR} -follow -type f -name '*.a' -delete \
        && find ${CONDA_DIR} -follow -type f -name '*.js.map' -delete \
        ; fi

RUN echo "Checking for 'start'..." \
        ; [ -d binder ] && cd binder \
        ; [ -d .binder ] && cd .binder \
        ; if test -f "start" ; then \
        chmod +x start \
        && cp start /srv/start \
        ; fi

EXPOSE 8888
ENTRYPOINT ["/srv/start"]
