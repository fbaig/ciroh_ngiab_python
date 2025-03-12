# Image compiled locally. NOT available on repo yet
FROM pangeo-notebook-rocky:latest

USER root
ENV PATH=${NB_PYTHON_PREFIX}/bin:$PATH

# Install necessary dependencies
RUN dnf install -y epel-release && \
    dnf install -y \
    dbus-x11 \
    firefox \
    xfce4-panel \
    xfce4-session \
    xfce4-settings \
    xorg-x11-server-Xorg \
    xorg-x11-xauth \
    xorg-x11-utils \
    xorg-x11-fonts-Type1 \
    nodejs \
    git \
    wget && \
    dnf clean all

# Install TurboVNC
ARG TURBOVNC_VERSION=2.2.6
RUN wget -q "https://sourceforge.net/projects/turbovnc/files/${TURBOVNC_VERSION}/turbovnc-${TURBOVNC_VERSION}.x86_64.rpm/download" -O turbovnc.rpm \
    && dnf install -y ./turbovnc.rpm \
    && rm -f turbovnc.rpm \
    && ln -s /opt/TurboVNC/bin/* /usr/local/bin/
#RUN dnf update -y && \
#    dnf install -y turbovnc tigervnc-server xorg-x11-fonts-Type1 xorg-x11-fonts-misc && \
#    dnf clean all


# Install mamba and websockify
RUN curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh \
    && /opt/conda/bin/conda create -n ${CONDA_ENV} -y -c conda-forge mamba websockify \
    #&& /opt/conda/bin/conda install -n ${CONDA_ENV} -y -c conda-forge mamba websockify \
    && /opt/conda/bin/conda clean -afy

# Install jupyter-remote-desktop-proxy with compatible npm version
RUN export PATH=${NB_PYTHON_PREFIX}/bin:${PATH} \
    && npm install -g npm@7.24.0 \
    && pip install --no-cache-dir \
        https://github.com/jupyterhub/jupyter-remote-desktop-proxy/archive/main.zip

# Install jupyterlab_vim and other extensions
RUN pip install jupyterlab_vim jupyter-tree-download

# Install Google Cloud SDK
RUN dnf install -y dnf-utils \
    && tee -a /etc/yum.repos.d/google-cloud-sdk.repo <<EOM
[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM
#    && tee -a /etc/yum.repos.d/google-cloud-sdk.repo <<EOM
#[google-cloud-cli]
#name=Google Cloud CLI
#baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64
#enabled=1
#gpgcheck=1
#repo_gpgcheck=0
#gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
#EOM
RUN dnf install -y google-cloud-cli

# Install additional Python packages
RUN pip install spatialpandas easydev colormap colorcet duckdb dask_geopandas hydrotools sidecar

# Upgrade colorama to resolve dependency conflict
RUN pip install --upgrade colorama

# Install nb_black separately to address metadata generation issue
RUN pip install nb_black==1.0.5

# Gfortran support (Rocky Linux equivalent)
RUN dnf update -y && \
    dnf install -y python3 python3-pip make cmake gcc gcc-gfortran libgcc libgcc.i686 netcdf-devel netcdf-fortran-devel openmpi-devel && \
    dnf clean all

RUN pip3 install numpy pandas xarray netcdf4 joblib toolz pyyaml Cython

# Install nbfetch for hydroshare
RUN pip install -U --no-cache-dir --upgrade-strategy only-if-needed git+https://github.com/hydroshare/nbfetch.git@hspuller-auth
# enable jupyter_server extension
RUN jupyter server extension enable --py nbfetch --sys-prefix

# Install google cloud bigquery
RUN pip install google-cloud-bigquery

# Update custom Jupyter Lab settings
RUN sed -i 's/\"default\": true/\"default\": false/g' /srv/conda/envs/notebook/share/jupyter/labextensions/@axlair/jupyterlab_vim/schemas/@axlair/jupyterlab_vim/plugin.json

# Install dataretrieval package
RUN pip install dataretrieval

# Assuming NB_USER is defined in your build context or as an ARG.
# If not, you may need to define it here or remove this line.
USER ${NB_USER}