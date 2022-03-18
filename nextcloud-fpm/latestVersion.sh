#!/bin/bash

docker tag netzint/nextcloud-fpm:$1 netzint/nextcloud-fpm:latest
docker push netzint/nextcloud-fpm:latest