#!/bin/bash

echo "this deletes everything!!!! Dont do it!"
echo "proceed? [y]"
read answer

if [ $answer == "y" ];then 

	rm -Rf -v ./db01-data/*
	rm -Rf -v ./db02-data/*
	rm -Rf -v ./nextcloud-persistant/data/*
	rm -Rf -v ./nextcloud-persistant/config/*
	rm -Rf -v ./nextcloud-persistant/custom_apps/*
	
	
	docker rm nextcloud_docker_cluster_nc-proxy01_1
	docker rm nextcloud_docker_cluster_nc-web01_1
	docker rm nextcloud_docker_cluster_nc-web02_1
	docker rm nextcloud_docker_cluster_nc-web03_1
	docker rm nextcloud_docker_cluster_nc-web04_1
	
	docker rm nextcloud_docker_cluster_app_1
	docker rm nextcloud_docker_cluster_app01_1
	docker rm nextcloud_docker_cluster_app02_1
	docker rm nextcloud_docker_cluster_app03_1
	docker rm nextcloud_docker_cluster_app04_1
	
	docker rm nextcloud_docker_cluster_fpm1
	docker rm nextcloud_docker_cluster_fpm01_1
	docker rm nextcloud_docker_cluster_fpm02_1
	docker rm nextcloud_docker_cluster_fpm03_1
	docker rm nextcloud_docker_cluster_fpm04_1
	
	docker rm nextcloud_docker_cluster_nc-sqlbroker_1
	docker rm nextcloud_docker_cluster_nc-db01_1
	docker rm nextcloud_docker_cluster_nc-db02_1
	docker rm nextcloud_docker_cluster_redis01_1
else
	echo "abort..."
fi
