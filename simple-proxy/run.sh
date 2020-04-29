#!/usr/bin/with-contenv bashio

CONFIG_PATH=/data/options.json

PROXY_PORT=$(jq --raw-output ".proxy_port" $CONFIG_PATH)
PROXY_SERVER=$(jq --raw-output ".proxy_server" $CONFIG_PATH)
PROXY_SERVER_PORT=$(jq --raw-output ".proxy_server_port" $CONFIG_PATH)

while [[ true ]]; do
    sleep 1
done