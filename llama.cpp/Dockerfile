ARG UBUNTU_VERSION=22.04
# This needs to generally match the container host's environment.
# We use a slightly older version for greater compatibility
ARG CUDA_VERSION=12.3.2
# CUDA build image
ARG CUDA_DEV_CONTAINER=nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}
# CUDA runtime image
ARG CUDA_RUN_CONTAINER=nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu${UBUNTU_VERSION}
# CUDA base image (excludes cublas)
ARG CUDA_BASE_CONTAINER=nvidia/cuda:${CUDA_VERSION}-base-ubuntu${UBUNTU_VERSION}

# use 2 stage build
ARG BUILD_IMAGE=ahoylabs/llama.cpp-base
FROM ${BUILD_IMAGE} as build

FROM ${CUDA_BASE_CONTAINER} as runtime

# copy server and batched bench
RUN mkdir -p /llama.cpp
COPY --from=build /llama.cpp/llama-server /llama.cpp/llama-batched-bench /llama.cpp/

RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get install -y $@ --no-install-recommends && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_install_clean.sh && \
    chmod a+x /usr/local/sbin/apt_install_clean.sh
RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get remove -y $@ && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_remove_clean.sh && \
    chmod a+x /usr/local/sbin/apt_remove_clean.sh

# we need just CUDA and CUBLAS
# this saves ~1GB vs the -runtime image
RUN /usr/local/sbin/apt_install_clean.sh libcublas-12-3 libcurl4 libgomp1 openssh-server wget screen curl nano python3

# install runpod python module for SERVERLESS
RUN /usr/local/sbin/apt_install_clean.sh python3-pip && pip3 install runpod && /usr/local/sbin/apt_remove_clean.sh python3-pip

# ENV variables

# you should override this, defaults to a small file
ENV LLAMA_MU="https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"

# this parameter is useful for performance tuning
# recommend 2048 for 40GB+ VRAM, 1024 for 24GB VRAM, 512 for less
ENV LLAMA_UB="1024"

# set this to "" to disable flash attention
ENV LLAMA_FA="-fa"
ENV LLAMA_CONTEXT="4096"

# quantized KV, note these require flash attention, eg "q8_0" or "q5_1"
ENV LLAMA_CTK=""
ENV LLAMA_CTV=""

ENV LLAMA_ROPE_FREQ_SCALE="1"
ENV LLAMA_PORT="8080"
ENV LLAMA_NP="1"
# lots of http threads for monitoring as well as network scan mitigation
ENV LLAMA_THREADS_HTTP="128"

# set API KEY if desired
ENV LLAMA_API_KEY=""
ENV LLAMA_NGL="-ngl 200"
ENV LLAMA_ADDITIONAL_ARGS="--metrics --host 0.0.0.0 -cb"

# default mode - just run server
# MODE=BENCH_FIRST - run a short batched-bench to help validate hardware
# MODE=SLEEP - just sleep infinity, allowing shell login to run manual commands
# MODE=SERVERLESS - RunPod Serverless mode
ENV MODE=""

# mount volume here
ENV WORKSPACE="/workspace"

COPY entry.sh runpod_rc.sh curl_loop.sh llama.cpp-handler.py /
ENTRYPOINT [ "./entry.sh" ]
