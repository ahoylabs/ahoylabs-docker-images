#!/usr/bin/python3

import runpod
import requests
import json
import time
import os
import aiohttp
import asyncio
import httpx

LOCAL_URL="http://localhost:8080/completion"
# read $LLAMA_NP from environment
ENV_DEBUG = os.environ.get('DEBUG')



log = runpod.RunPodLogger()


def wait_for_service(url):
    '''
    Check if the service is ready to receive requests.
    '''
    log.info("Checking if service is ready..")
    while True:
        try:
            requests.get(url, timeout=120)
            return
        except requests.exceptions.RequestException:
            log.debug("Service not ready yet. Retrying after .1s sleep...")
        except Exception as err:
            log.error("Error: ", err)
        time.sleep(.1)


llama_stream_completion_session = None

async def stream_completion(job):
    global llama_stream_completion_session

    # Initialize the session if not already initialized
    if llama_stream_completion_session is None:
        llama_stream_completion_session = aiohttp.ClientSession()
    job_id = job["id"]
    job_input = job["input"]
    job_input["stream"] = True # ensure the llama server streams output
    log.info("Received stream completion job with id " + job_id)

    async with llama_stream_completion_session.post(LOCAL_URL, data=json.dumps(job_input)) as response:
        if response.status != 200:
            raise ValueError(f"HTTP Error: {response.status}")
        async for line in response.content:
            # readlines returns empty bytes array at EOF
            if line == b'' and response.content.at_eof():
                yield b'EOF'
                log.info("Reached EOF for job with id " + job_id)
            else:
                yield line
# async def stream_completion2(job):
#     job_id = job["id"]
#     job_input = job["input"]
#     job_input["stream"] = True # ensure the llama server streams output
#     log.info("Received stream completion job with id " + job_id)
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(LOCAL_URL, data=json.dumps(job_input)) as response:
#             if response.status != 200:
#                 raise ValueError(f"HTTP Error: {response.status}")
#             async for line in response.content:
#                 yield line


def completion(job):
    job_id = job["id"]
    job_input = job["input"]
    # for the serverless handler, we need to disable streaming
    job_input["stream"] = False  # Adding "stream": false to the job input
    log.info("Received completion job with id " + job_id)
    try:
        response = requests.post(LOCAL_URL, json=job_input)
        if response.status_code == 200:
            log.info("Response received for job with id " + job_id)
            return response.json()
        else:
            log.error("Error: Failed sending to llama.cpp Status code:", response.status_code)
            return {"error": "Error, response code " + response.status_code}
    except Exception as e:
        log.error("Error:", e)
        return {"error": "Error: " + e}


async def old_httpx(job):
    job_id = job["id"]
    job_input = job["input"]
    job_input["stream"] = True # ensure the llama server streams output
    log.info("Received stream completion job with id " + job_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(LOCAL_URL, json=job_input)
        async for chunk in response.aiter_text():
            yield chunk
        log.info("Stream completion job finished, id " + job_id)


async def new_httpx(job):
    job_id = job["id"]
    job_input = job["input"]
    job_input["stream"] = True
    log.info("Received async completion job with id " + job_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(LOCAL_URL, json=job_input)
        async for line in response.aiter_lines():
            yield line
        log.info("Stream completion job finished, id " + job_id)


def get_np():
    try:
        llama_np = int(os.environ.get('LLAMA_NP'))
        if llama_np > 1:
            log.info("Using concurrency " + str(llama_np))
            return llama_np
    except (TypeError, ValueError):
        log.info("Invalid LLAMA_NP value, using default concurrency 1")
    # Default to 1 if LLAMA_NP is blank, <1, or not an integer
    return 1


async def streaming_test():
    test_input = {
        "id": "manual test input",
        "input": {
            "n_predict": 10,
            "prompt": "Tell me about llamas"
        }
    }
    async for line in stream_completion(test_input):
        print(line)


# select handler based on ENV
ENV_RUNPOD_HANDLER = os.environ.get('RUNPOD_HANDLER')
ENV_LLAMA_NP = get_np()

if ENV_RUNPOD_HANDLER == "ASYNC_GENERATOR":
    selected_handler = stream_completion
elif ENV_RUNPOD_HANDLER == "OLD_HTTPX":
    selected_handler = old_httpx
elif ENV_RUNPOD_HANDLER == "NEW_HTTPX":
    selected_handler = new_httpx
else:
    selected_handler = completion

wait_for_service(LOCAL_URL)
log.info("Executing streaming test..")
# Run the manual test
if ENV_DEBUG == "TRUE":
    print ("DEBUG=TRUE, executing streaming_test()")
    asyncio.run(streaming_test())

log.info("Service ready, starting up handler")
if ENV_LLAMA_NP is not None:
    log.info("Env variable LLAMA_NP detected as " +  ENV_LLAMA_NP)
#runpod.serverless.start({"handler": completion})
runpod.serverless.start(
    {
        "handler": selected_handler,
#        "handler": completion,
        "return_aggregate_stream": True,  # Optional, results available via /run
        "concurrency_modifier": lambda x: ENV_LLAMA_NP,
    }
)
