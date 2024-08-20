#!/bin/bash

echo "-> gc-controller::sleep"
curl --location --request PUT 'http://'$1':3000/gc-controller/sleep' \
--header 'Content-Type: application/json' \
--data '{
    "count": 2
}'