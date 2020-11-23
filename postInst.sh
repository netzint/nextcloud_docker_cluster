#!/bin/bash

source db.env


docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-primary-keys
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ background:cron

