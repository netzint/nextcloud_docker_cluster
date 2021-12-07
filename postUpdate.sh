#!/bin/bash

source db.env

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ upgrade
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-indices
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:convert-filecache-bigint

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ config:system:set default_phone_region --value $PHONE_REGION

