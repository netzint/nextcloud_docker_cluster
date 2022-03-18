#!/bin/bash

while read line; do
  if [[ $line = \#* ]] ; then
      continue
  fi
  echo "Building nextcloud image with version $line"
  sed -i "s/FROM .*/FROM nextcloud:$line-fpm/g" Dockerfile
  docker build -t netzint/nextcloud-fpm:$line .
  docker push netzint/nextcloud-fpm:$line
done <versions.txt
