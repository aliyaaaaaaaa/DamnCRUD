#!bin/bash

until $(curl --output /dev/null --silent --head --fail http://localhost:4444); do
    echo "waiting for the hub to start"
    sleep 1
done