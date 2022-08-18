#!/bin/bash

cp db.env.example db.env

sed -i "s/MYSQL_ROOT_PASSWORD=.*/MYSQL_ROOT_PASSWORD=$(date +%s | sha256sum | base64 | head -c 32)/g" db.env
sed -i "s/MYSQL_PASSWORD=.*/MYSQL_PASSWORD=$(date +%s | sha512sum | base64 | head -c 32)/g" db.env
