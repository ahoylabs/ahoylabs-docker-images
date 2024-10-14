#!/usr/bin/python3

import aiohttp
import asyncio
import json
import httpx

HEALTH_URL="http://localhost:8080/health"
COMPLETION_URL="http://localhost:8080/completion"

test_input = {
    "id": "manual test input",
    "input": {
        "n_predict": 10,
        "prompt": "Tell me about llamas"
    }
}


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(HEALTH_URL) as resp:
            print(resp.status)
            print(await resp.text())

async def post(job):
    job_id = job["id"]
    job_input = job["input"]
    job_input["stream"] = True # ensure the llama server streams output
    print("Received stream completion job with id " + job_id)

    async with aiohttp.ClientSession() as session:
        async with session.post(COMPLETION_URL, data=json.dumps(job_input)) as resp:
            print(resp.status)
            print(await resp.text())

async def stream_completion(job):
    job_id = job["id"]
    job_input = job["input"]
    job_input["stream"] = True # ensure the llama server streams output
    print("Received stream completion job with id " + job_id)

    async with aiohttp.ClientSession() as session:
        async with session.post(COMPLETION_URL, data=json.dumps(job_input)) as resp:
            async for line in resp.content:
                yield line


async def streaming_test():
    async for line in stream_completion(test_input):
        print(line)


asyncio.run(main())
#asyncio.run(post(test_input))
asyncio.run(streaming_test())
