#!/bin/bash

source samba.env


docker cp templates/externalStorage.json nextcloud_docker_cluster_fpm01_1:/
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ files_external:import /externalStorage.json

