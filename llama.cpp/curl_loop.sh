#!/bin/sh

# simple script to assist in testing

do_curl() {
  curl --location 'http://localhost:8080/completion' \
  --header 'Content-Type: application/json' \
  --data '{
      "stream": true,
      "prompt": "Tell me about llamas."
  }' > /dev/null 2>&1
}

while [ 1 ]; do
  do_curl
done
