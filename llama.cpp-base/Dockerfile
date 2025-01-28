# llama tag or commit to checkout
ARG LLAMA_COMMIT=b4562

ARG UBUNTU_VERSION=22.04
# This needs to generally match the container host's environment.
# We use a slightly older version for greater compatibility
ARG CUDA_VERSION=12.3.1
# CUDA build image
ARG CUDA_DEV_CONTAINER=nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}
# CUDA runtime image
ARG CUDA_RUN_CONTAINER=nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu${UBUNTU_VERSION}
# CUDA base image (excludes cublas)
ARG CUDA_BASE_CONTAINER=nvidia/cuda:${CUDA_VERSION}-base-ubuntu${UBUNTU_VERSION}

FROM ${CUDA_DEV_CONTAINER} AS build


RUN apt-get update && \
    apt-get install -y build-essential git libcurl4-openssl-dev ccache cmake

WORKDIR /app

RUN echo "checking out llama.cpp and commit or tag LLAMA_COMMIT=${LLAMA_COMMIT}"
RUN git clone https://github.com/ggerganov/llama.cpp.git . && git checkout ${LLAMA_COMMIT}

# try more targetted build
# try targeting 80, the A100's version
# this supports all ampere and later GPUs
# Set nvcc architecture
ENV FLAG_ARCH="CMAKE_CUDA_ARCHITECTURES=80"
# Enable CUDA
ENV FLAG_CUDA="GGML_CUDA=ON"
# Enable cURL
ENV FLAG_CURL="LLAMA_CURL=ON"
# Enable quantized kv
ENV FLAG_QUANTS="GGML_CUDA_FA_ALL_QUANTS=ON"
# Static builds
ENV FLAG_STATIC="BUILD_SHARED_LIBS=OFF"

# CMake Configuration Step
RUN cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -D${FLAG_ARCH} \
  -D${FLAG_CUDA} \
  -D${FLAG_CURL} \
  -D${FLAG_QUANTS} \
  -D${FLAG_STATIC}

#Unclear if cmake honors env vars
RUN cmake --build build --target llama-batched-bench llama-server --config Release -j 12

FROM ${CUDA_BASE_CONTAINER} AS runtime

RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get install -y $@ && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_install_clean.sh && \
    chmod a+x /usr/local/sbin/apt_install_clean.sh
RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get remove -y $@ && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_remove_clean.sh && \
    chmod a+x /usr/local/sbin/apt_remove_clean.sh

# we need just CUDA and CUBLAS
# this saves ~1GB vs the -runtime image
RUN /usr/local/sbin/apt_install_clean.sh libcublas-12-3 libcurl4 libgomp1

# copy server and batched bench
RUN mkdir -p /llama.cpp
COPY --from=build /app/build/bin/llama-server /app/build/bin/llama-batched-bench /llama.cpp/

ENTRYPOINT [ "/llama.cpp/llama-server" ]
