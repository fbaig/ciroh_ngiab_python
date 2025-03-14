FROM ubuntu:22.04 AS base

ENV TROUTE_REPO=CIROH-UA/t-route
ENV TROUTE_BRANCH=ngiab
ENV NGEN_REPO=CIROH-UA/ngen
ENV NGEN_BRANCH=ngiab

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    vim gfortran sqlite3 \
    bzip2 libexpat1-dev libudunits2-dev zlib1g-dev \
    mpich libhdf5-dev libnetcdf-dev libnetcdff-dev libnetcdf-c++4-dev

FROM base AS build_base

RUN apt-get update && apt-get install -y \
    sudo gcc-11 g++-11 make cmake ninja-build tar git gfortran \
    python3 python3-dev python3-pip \
    flex bison wget

FROM build_base AS boost_build
WORKDIR /
RUN wget https://archives.boost.io/release/1.79.0/source/boost_1_79_0.tar.gz
RUN tar -xzf boost_1_79_0.tar.gz
WORKDIR /boost_1_79_0
RUN ./bootstrap.sh && ./b2 && ./b2 headers
ENV BOOST_ROOT=/boost_1_79_0

FROM boost_build AS troute_prebuild
WORKDIR /ngen
ENV FC=gfortran NETCDF=/usr/include
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install uv && uv venv
ENV PATH="/ngen/.venv/bin:$PATH"
ADD https://api.github.com/repos/${TROUTE_REPO}/git/refs/heads/${TROUTE_BRANCH} /tmp/version.json
RUN uv pip install -r https://raw.githubusercontent.com/$TROUTE_REPO/refs/heads/$TROUTE_BRANCH/requirements.txt

FROM troute_prebuild AS troute_build
WORKDIR /ngen/t-route
RUN git clone --depth 1 --single-branch --branch $TROUTE_BRANCH https://github.com/$TROUTE_REPO.git .
RUN git submodule update --init --depth 1
RUN uv pip install build wheel
RUN sed -i 's/build_[a-z]*=/#&/' compiler.sh
RUN ./compiler.sh no-e
#### TROUTE ####
#RUN uv pip install --config-setting='--build-option=--use-cython' src/troute-network/
#RUN uv build --wheel --config-setting='--build-option=--use-cython' src/troute-network/
#RUN uv pip install --no-build-isolation --config-setting='--build-option=--use-cython' src/troute-routing/
#RUN uv build --wheel --no-build-isolation --config-setting='--build-option=--use-cython' src/troute-routing/
#RUN uv build --wheel --no-build-isolation src/troute-config/
#RUN uv build --wheel --no-build-isolation src/troute-nwm/

FROM troute_prebuild AS ngen_clone
WORKDIR /ngen
ADD https://api.github.com/repos/${NGEN_REPO}/git/refs/heads/${NGEN_BRANCH} /tmp/version.json
RUN git clone --single-branch --branch $NGEN_BRANCH https://github.com/$NGEN_REPO.git && \
    cd ngen && \
    git submodule update --init --recursive --depth 1

FROM ngen_clone AS ngen_build
ENV PATH=${PATH}:/usr/bin/mpich
WORKDIR /ngen/ngen

RUN apt-get update && apt-get install -y libsqlite3-dev
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
    -DCMAKE_INSTALL_PREFIX=."

RUN cmake -G Ninja -B cmake_build_serial -S . ${COMMON_BUILD_ARGS} -DNGEN_WITH_MPI:BOOL=OFF && \
    cmake --build cmake_build_serial --target all -- -j $(nproc)

ARG MPI_BUILD_ARGS="-DNGEN_WITH_MPI:BOOL=ON \
    -DNetCDF_ROOT=/usr/lib/x86_64-linux-gnu \
    -DCMAKE_PREFIX_PATH=/usr/lib/x86_64-linux-gnu"

RUN cmake -G Ninja -B cmake_build_parallel -S . ${COMMON_BUILD_ARGS} ${MPI_BUILD_ARGS} && \
    cmake --build cmake_build_parallel --target all -- -j $(nproc)

FROM ngen_build AS restructure_files
RUN mkdir -p /dmod/datasets /dmod/datasets/static /dmod/shared_libs /dmod/bin && \
    cp -a ./extern/**/cmake_build/*.so* /dmod/shared_libs/. || true && \
    cp -a ./extern/noah-owp-modular/**/*.TBL /dmod/datasets/static && \
    cp -a ./cmake_build_parallel/ngen /dmod/bin/ngen-parallel || true && \
    cp -a ./cmake_build_serial/ngen /dmod/bin/ngen-serial || true && \
    cp -a ./cmake_build_parallel/partitionGenerator /dmod/bin/partitionGenerator || true && \
    cd /dmod/bin && \
    (stat ngen-parallel && ln -s ngen-parallel ngen) || (stat ngen-serial && ln -s ngen-serial ngen)

FROM restructure_files AS final
WORKDIR /ngen
COPY HelloNGEN.sh /ngen/HelloNGEN.sh
COPY --from=restructure_files /dmod /dmod
#### TROUTE ####
#COPY --from=troute_build /ngen/t-route/src/troute-*/dist/*.whl /tmp/
RUN ln -s /dmod/bin/ngen /usr/local/bin/ngen
ENV UV_INSTALL_DIR=/root/.cargo/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

#### TROUTE ####
#RUN uv self update && uv venv && \
#    uv pip install --no-cache-dir /tmp/*.whl netCDF4==1.6.3

RUN rm -rf /tmp/*.whl
RUN echo "/dmod/shared_libs/" >> /etc/ld.so.conf.d/ngen.conf && ldconfig -v
ENV PATH=$PATH:/usr/bin/mpich
RUN chmod a+x /dmod/bin/* /ngen/HelloNGEN.sh
RUN uv pip install numpy==$(/dmod/bin/ngen --info | grep -e 'NumPy Version: ' | cut -d ':' -f 2 | uniq | xargs)
ENV PATH="/ngen/.venv/bin:${PATH}"
COPY --from=ngen_clone /ngen/ngen/extern/lstm/lstm /ngen/ngen/extern/lstm
RUN uv pip install --no-cache-dir /ngen/ngen/extern/lstm --extra-index-url https://download.pytorch.org/whl/cpu
#COPY --from=troute_build /tmp/troute_url /ngen/troute_url
#COPY --from=ngen_build /tmp/ngen_url /ngen/ngen_url
RUN echo "export PS1='\u\[\033[01;32m\]@ngiab_dev\[\033[00m\]:\[\033[01;35m\]\W\[\033[00m\]\$ '" >> ~/.bashrc
ENTRYPOINT ["./HelloNGEN.sh"]
