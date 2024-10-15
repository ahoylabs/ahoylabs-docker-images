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

FROM ghcr.io/ggerganov/whisper.cpp:main-cuda AS whisper

FROM ${CUDA_BASE_CONTAINER} AS runtime

COPY --from=whisper /app/server /app/models/download-ggml-model.sh /app/

RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get install -y $@ --no-install-recommends && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_install_clean.sh && \
    chmod a+x /usr/local/sbin/apt_install_clean.sh
RUN /bin/echo -e '#!/bin/bash\nDEBIAN_FRONTEND=noninteractive\napt-get update && apt-get remove -y $@ && apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/apt/lists/*' \
    > /usr/local/sbin/apt_remove_clean.sh && \
    chmod a+x /usr/local/sbin/apt_remove_clean.sh

# we need just CUDA and CUBLAS
# this saves ~1GB vs the -runtime image
RUN /usr/local/sbin/apt_install_clean.sh libcublas-12-3 curl wget ffmpeg

ENV MODEL="small-q5_1"
ENV PORT="8200"
ENV ADDITIONAL_ARGS="--host 0.0.0.0 --convert --inference-path /whisper"

# mount volume here
ENV WORKSPACE="/workspace"

COPY entry.sh /
ENTRYPOINT [ "/entry.sh" ]
