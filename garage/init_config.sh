#!/bin/sh
set -e 

CONFIG_FILE="/etc/garage.toml"

if [ -f "$CONFIG_FILE" ]; then
    echo "Garage config already exists at ${CONFIG_FILE}. Skipping creation."
else
    echo "Garage config not found. Creating new config at ${CONFIG_FILE}..."
    cat > "$CONFIG_FILE" <<EOF
metadata_dir = "/etc/garage/meta"
data_dir = "/etc/garage/data"
db_engine = "sqlite"

replication_factor = 1

rpc_bind_addr = "[::]:3901"
rpc_public_addr = "127.0.0.1:3901"
rpc_secret = "$(openssl rand -hex 32)"

[s3_api]
api_bind_addr = "[::]:3900"
s3_region = "garage"
root_domain = ".s3.garage.localhost"

[admin]
api_addr = "[::]:3903"
admin_token = "$(openssl rand -base64 32)"
EOF
    
    echo "Garage config created."
fi