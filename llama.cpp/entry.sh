#!/bin/sh

# we expect the following env variables
# MU="https://huggingface.co/TheBloke/TinyLlama-1.1B-1T-OpenOrca-GGUF/resolve/main/tinyllama-1.1b-1t-openorca.Q4_0.gguf"
# UB="1024"
# FA="-fa"
# CONTEXT="4096"
# ROPE_FREQ_SCALE="1"
# PORT="8080"
# NP="1"
# API_KEY=""
# ADDITIONAL_ARGS="--metrics --host 0.0.0.0 -ngl 200 -cb"

# set WORKSPACE to "/" if $WORKSPACE not a directory/doesn't exist
if [ ! -d "$WORKSPACE" ]; then
  WORKSPACE="/"
fi

# MU might be blank, if so try to load $WORKSPACE/models/model.gguf
if [ -z "$LLAMA_MU" ]; then
  filename="${WORKSPACE}/models/model.gguf"
  MODEL_ARG="-m $filename"
else
  modelfile=`echo $LLAMA_MU | awk -F "/" '{print $NF}'`
  filename="${WORKSPACE}/models/$modelfile"
  MODEL_ARG="-mu $LLAMA_MU"
fi

if [ ! -z "$LLAMA_UB" ]; then
  UB_ARG="-b $LLAMA_UB -ub $LLAMA_UB"
fi

if [ ! -z "$LLAMA_CTK" ]; then
  CTK_ARG="-ctk $LLAMA_CTK"
fi

if [ ! -z "$LLAMA_CTV" ]; then
  CTV_ARG="-ctv $LLAMA_CTV"
fi

if [ ! -z "$LLAMA_API_KEY" ]; then
  API_KEY_ARG="--api-key $LLAMA_API_KEY"
fi

## Start up
set -x

if [ "$MODE" = "SERVERLESS" ]; then
  # this should be a mounted network storage
  MODEL_ARG="-m $filename"
  # launch handler, it will wait for server to become ready
  echo "Launching RunPod Serverless handler.."
  /llama.cpp-handler.py > /dev/null &
else
  # these are useful for static instance
  # but we don't want them for SERVERLESS MODE
  . ./runpod_rc.sh
  echo "Executing RunPod functions.."
  setup_ssh
  export_env_vars
fi

cd $WORKSPACE
mkdir -p models
# set the LLAMA_CACHE variable, as this is now where models are saved
export LLAMA_CACHE=$WORKSPACE/models

# add sleep option
if [ "$MODE" = "SLEEP" ]; then
  /usr/bin/sleep infinity
  exit
# this probably doesn't work right now
elif [ "$MODE" = "BENCH_FIRST" ]; then
  # if we auto restart after crash, don't run benchmark
  CHECK_FILE=$WORKSPACE/bench_complete
  if [ ! -f "$CHECKFILE" ]; then
    echo Downloading $filename and running short benchmark
    cd $WORKSPACE/models && wget $LLAMA_MU
    cd $WORKSPACE && /llama.cpp/llama-batched-bench models/$filename $LLAMA_CONTEXT $LLAMA_UB $LLAMA_UB 0 0 999 2048 256 1,1,1,1,2
    echo benchmark complete, running /llama.cpp/llama-server in 5 seconds..
    touch $CHECK_FILE
    sleep 5
  fi
fi

/llama.cpp/llama-server $MODEL_ARG $LLAMA_FA $UB_ARG -c $LLAMA_CONTEXT -t $LLAMA_NP \
  -np $LLAMA_NP $LLAMA_NGL --rope-freq-scale $LLAMA_ROPE_FREQ_SCALE \
  --port $LLAMA_PORT $LLAMA_ADDITIONAL_ARGS $API_KEY_ARG $CTK_ARG $CTV_ARG \
  --threads-http $LLAMA_THREADS_HTTP
