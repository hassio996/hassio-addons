#!/usr/bin/with-contenv bashio

CONFIG_PATH=/data/options.json

# HOST=$(jq --raw-output ".frp_server" $CONFIG_PATH)
# PORT=$(jq --raw-output ".frp_server_port" $CONFIG_PATH)
# TOKEN=$(jq --raw-output ".frp_token" $CONFIG_PATH)
# SERVER_LOCAL=$(jq --raw-output ".local_host" $CONFIG_PATH)
# PORT_LOCAL=$(jq --raw-output ".local_port" $CONFIG_PATH)
# TYPE=$(jq --raw-output ".tunnel_type" $CONFIG_PATH)

# HTTP_DOMAIN=$(jq --raw-output ".http_domain" $CONFIG_PATH)
# HTTP_SUBDOMAIN_HOST=$(jq --raw-output ".http_subdomain_host" $CONFIG_PATH)
# TCP_PORT_REMOTE=$(jq --raw-output ".tcp_remote_port" $CONFIG_PATH)

python3 -m http.server -d /audio/ 8000 > /dev/null 2>&1 &

python3 run.py 2>&1

#while [[ true ]]; do
#    sleep 1
#done