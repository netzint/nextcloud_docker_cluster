#!/bin/bash

case "$1" in
  start)
	docker-compose up -d 
        ;;
  stop)
	echo "stop db2"
	docker stop nextcloud_docker_cluster_nc-db02_1
	echo "wait for cluster to sync"
	sleep 20
	docker-compose down
	;;

  *)
	echo "$1 not supported"
	echo "use start or stop"
	;;


esac

