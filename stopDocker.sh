#!/bin/bash

echo "stop db2"
docker stop nextcloud_docker_cluster_nc-db02_1
echo "wait for cluster to sync"
sleep 20
docker-compose down
