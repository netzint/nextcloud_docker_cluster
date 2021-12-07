#!/bin/bash
source ./db.env

sed -i "s/add_header X-Frame-Options \"SAMEORIGIN\";/#add_header X-Frame-Options \"SAMEORIGIN\";/g" web/web*/nextcloud
sed -i "/add_header X-Frame-Options \"SAMEORIGIN\";/i \    add_header X-Frame-Options \"ALLOW-FROM $SERVER_URL\";\n    add_header Content-Security-Policy \"frame-ancestors $SERVER_URL\";" web/web*/nextcloud

docker exec nextcloud_docker_cluster_fpm01_1 sed -i "/allowedFrameAncestors = \[/a \                '$SERVER_URL'," /var/www/html/lib/public/AppFramework/Http/ContentSecurityPolicy.php
docker exec nextcloud_docker_cluster_fpm01_1 sed -i "s/\[\]/['$SERVER_URL']/g" /var/www/html/lib/public/AppFramework/Http/ContentSecurityPolicy.php

sed -i "/docker-compose up -d/a \        sleep 20\n        ./allowFraming.sh" daemonHandler.sh


