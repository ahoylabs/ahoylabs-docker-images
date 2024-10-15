#!/bin/sh

# we expect the following env variables
# MODEL="small-q5_1"
# PORT="8080"
# ADDITIONAL_ARGS="--metrics --host 0.0.0.0--convert --inference-path /whisper"

# also handle create /public and populate

# set WORKSPACE to "/" if $WORKSPACE not a directory/doesn't exist
if [ ! -d "$WORKSPACE" ]; then
  WORKSPACE="/"
fi

cd $WORKSPACE
mkdir -p models

if [ ! -f "models/ggml-${MODEL}.bin" ]; then
  /app/download-ggml-model.sh $MODEL /models
fi
MODEL_ARG="-m $WORKSPACE/models/ggml-${MODEL}.bin"

# this is the path we use for health checks
mkdir -p public/v1
echo "alive" > public/v1/models
PUBLIC_ARG="--public $WORKSPACE/public"

/app/server $MODEL_ARG --port $PORT $ADDITIONAL_ARGS $PUBLIC_ARG