#!/bin/bash

echo "-> gc-controller::wake-up"
curl --location --request PUT 'http://'$1':3000/gc-controller/wake'