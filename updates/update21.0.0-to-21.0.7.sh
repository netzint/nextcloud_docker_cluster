#!/bin/bash

source db.env
fromVersion=21.0.0
toVersion=21.0.7

version=$(docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ status --output json | jq '.versionstring')

if [ $fromVersion != $version ]; then
	echo "ERROR: Wrong script started!"
	echo "Your are running $version"
	echo "This script updates $fromVersion to $toVersion"
	exit 1
fi

echo "Starting Update"
echo "This script updates $fromVersion to $toVersion"
echo "Press Ctrl C to abort, starting in 5 seconds"
sleep 5

./daemonHandler stop

# -> umschreiben dockerversion Dockerfile
sed -i "s/From.*/From nextcloud:$toVersion-fpm/g" nextcloud-fpm/Dockerfile
exit

./daemonHandler update

# add primaray key to database
mysql -h 127.0.0.1 -u nextcloud_db_user -p$MYSQL_PASSWORD -e 'CREATE TABLE oc_ratelimit_entries (hash VARCHAR(128) NOT NULL, delete_after DATETIME NOT NULL, INDEX ratelimit_hash (hash), INDEX ratelimit_delete_after (delete_after), PRIMARY KEY(hash)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_bin` ENGINE = InnoDB ROW_FORMAT = compressed;'

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ upgrade
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-indices
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:convert-filecache-bigint
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-primary-keys
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ db:add-missing-columns
docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ config:system:set default_phone_region --value $PHONE_REGION

docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ app:update --all

echo "You can exit maintenance by entering"
echo 'docker exec --user www-data -it nextcloud_docker_cluster_fpm01_1 /var/www/html/occ maintenance --off'