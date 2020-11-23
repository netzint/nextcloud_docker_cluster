#!/bin/bash

source db.env

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ maintenance:install -vvv --no-interaction \
    --database 'mysql' \
    --database-name $MYSQL_DATABASE \
    --database-user $MYSQL_USER \
    --database-pass $MYSQL_PASSWORD \
    --admin-user $NEXTCLOUD_ADMIN \
    --admin-pass $NEXTCLOUD_ADMIN_PASSWORD \
    --data-dir '/var/www/html/data' \
    --database-host nc-sqlbroker

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ config:system:set trusted_domains 1 --value= $INTERNAL_IP
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ config:system:set trusted_domains 2 --value= $INTERNAL_DOMAINNAME


docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-primary-keys
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ background:cron

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ app:disable firstrunwizard

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ app:enable user_ldap
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ app:enable files_external


