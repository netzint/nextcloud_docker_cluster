#!/bin/bash
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ files:scan --all > /srv/docker/nextcloud_docker_cluster/lastSyncLog.log
