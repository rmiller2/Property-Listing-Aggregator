#!/bin/bash

STATUS=$(curl -s -o /dev/null -w '%{http_code}' $1)
if [ $STATUS -eq 301 ]; then
  echo "We got a redirect"
  exit 1
elif [ $STATUS -eq 200 ]; then
  echo "Got $STATUS, success"
  exit 0
else
  echo "Got $STATUS, huh weird"
fi
