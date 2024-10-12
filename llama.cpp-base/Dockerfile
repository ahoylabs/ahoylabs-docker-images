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

FROM ${CUDA_DEV_CONTAINER} as build

# try more targetted build
# ARG CUDA_DOCKER_ARCH=all
# try targetind sm_80, the A100's version
# this supports all ampere and later GPUs
ARG CUDA_DOCKER_ARCH=sm_80

RUN apt-get update && \
    apt-get install -y build-essential git libcurl4-openssl-dev ccache

WORKDIR /app

RUN git clone https://github.com/ggerganov/llama.cpp.git . && git checkout b3853

# Set nvcc architecture
ENV CUDA_DOCKER_ARCH=${CUDA_DOCKER_ARCH}
# Enable CUDA
ENV LLAMA_CUDA=1
# Enable cURL
ENV LLAMA_CURL=1
# Enable quantized kv
ENV LLAMA_CUDA_FA_ALL_QUANTS=1

RUN make -j 12

FROM ${CUDA_BASE_CONTAINER} as runtime

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
COPY --from=build /app/llama-server /app/llama-batched-bench /llama.cpp/

ENTRYPOINT [ "/llama.cpp/llama-server" ]
