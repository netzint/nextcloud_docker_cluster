#!/bin/bash

source ../db.env
fromVersion=22.1.0
toVersion=22.2.3

docker ps  | grep nextcloud_docker_cluster > /dev/null
if [ $? -gt 0 ];then
        echo "Failed to get version, see of nextcloud_docker_cluster is running"
        exit 1
fi

version=$(docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ status | grep versionstring | awk -F ':'  '{print $2}')
version=$(echo $version | sed 's/"//g' | sed  's/\r$//g')
echo "This script updates $fromVersion to $toVersion"

if [ "$fromVersion" != "$version" ]; then
	echo "ERROR: Wrong script started!"
	echo "Your are running $version"
	echo "This script updates $fromVersion to $toVersion"
        exit 1
fi

echo "Starting Update"
echo "This script updates $fromVersion to $toVersion"
echo "Press Ctrl C to abort, starting in 5 seconds"
sleep 5

../daemonHandler.sh stop

# -> umschreiben dockerversion Dockerfile
echo "Creating override file"
echo "version: '3.8'
services:
  app:
    image: netzint/nextcloud-fpm:$toVersion
  fpm01:
    image: netzint/nextcloud-fpm:$toVersion
  fpm02:
    image: netzint/nextcloud-fpm:$toVersion
  fpm03:
    image: netzint/nextcloud-fpm:$toVersion
  fpm04:
    image: netzint/nextcloud-fpm:$toVersion
" > ../docker-compose.override.yml

echo "updating container"
docker-compose --project-directory ../ pull
../daemonHandler.sh start
echo "Waiting for nextcloud to start"
sleep 15


# add primaray key to database
mysql -h 127.0.0.1 -u nextcloud_db_user -p$MYSQL_PASSWORD nextcloud -e 'CREATE TABLE oc_ratelimit_entries (hash VARCHAR(128) NOT NULL, delete_after DATETIME NOT NULL, INDEX ratelimit_hash (hash), INDEX ratelimit_delete_after (delete_after), PRIMARY KEY (hash)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_bin` ENGINE = InnoDB ROW_FORMAT = compressed'

echo "upgrading nextcloud installation"
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ upgrade
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-indices
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:convert-filecache-bigint
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-primary-keys
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-columns
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ config:system:set default_phone_region --value $PHONE_REGION

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ app:update --all

echo "You can exit maintenance by entering"
echo 'docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ maintenance --off'
