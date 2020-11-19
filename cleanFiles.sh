#!/bin/bash
rm -Rf -v ./db01-data/*
rm -Rf -v ./db02-data/*
rm -Rf -v ./nextcloud/data/*

docker rm ni-nextcloud_nc-web04_1
docker rm ni-nextcloud_nc-web01_1
docker rm ni-nextcloud_nc-web02_1
docker rm ni-nextcloud_app_1
docker rm ni-nextcloud_nc-proxy01_1
docker rm ni-nextcloud_nc-db01_1
docker rm ni-nextcloud_redis01_1
docker rm ni-nextcloud_nc-db02_1
docker rm ni-nextcloud_nc-sqlbroker_1
