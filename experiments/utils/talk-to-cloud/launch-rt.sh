#!/bin/bash

## Set variables
#AUTH_URL="http://<KEYSTONE_URL>/v3"
#USERNAME="your_username"
#PASSWORD="your_password"
#PROJECT_NAME="your_project"
#DOMAIN_NAME="default"

# Get authentication token
TOKEN=$(curl -s -X POST $OS_AUTH_URL/auth/tokens \
-H "Content-Type: application/json" \
-d '{
    "auth": {
        "identity": {
            "methods": ["password"],
            "password": {
                "user": {
                    "name": "'$OS_USERNAME'",
                    "domain": { "name": "'$OS_DOMAIN_NAME'" },
                    "password": "'$OS_PASSWORD'"
                }
            }
        },
        "scope": {
            "project": {
                "name": "'$OS_PROJECT_NAME'",
                "domain": { "name": "'$OS_DOMAIN_NAME'" }
            }
        }
    }
}' -i | grep X-Subject-Token | awk '{print $2}')

curl 'http://localhost:8002/dashboard/api/nova/servers/' \
  -H "X-Auth-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{"availability_zone":"nova","config_drive":false,"user_data":"","default_user_data":"","disk_config":"AUTO","instance_count":1,"name":"RT-8","scheduler_hints":{"type":"evictable"},"security_groups":["default"],"create_volume_default":true,"hide_create_volume":false,"source_id":null,"block_device_mapping_v2":[{"source_type":"image","destination_type":"volume","delete_on_termination":true,"uuid":"2c99d25f-6cca-42a1-b678-06e85597f890","boot_index":"0","volume_size":10}],"flavor_id":"e9caecfe-ac1e-460d-bb74-bd724141d1a1","nics":[{"net-id":"a57f5c22-93c3-4b45-b9c1-f96b52fee360","v4-fixed-ip":""}],"key_name":"common-kp"}'

