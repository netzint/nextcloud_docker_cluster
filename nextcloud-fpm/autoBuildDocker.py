#!/usr/bin/env python3

###################################################
# Automaticly build Docker-Images for Nextcloud
# by lukas.spitznagel@netzint.de
# V1.0 from 2023/06/15
###################################################

import requests
import json
import re
import docker
import io
import os

DOCKERFILE_TEMPLATE="""
FROM nextcloud:##TAG##-fpm

RUN apt-get update && apt-get install -y supervisor smbclient libsmbclient-dev libgmp-dev libicu-dev sudo libmagickcore-6.q16-3-extra \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir /var/log/supervisord /var/run/supervisord

RUN pecl install smbclient
RUN docker-php-ext-enable smbclient
RUN docker-php-ext-install intl
RUN docker-php-ext-install gmp

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV NEXTCLOUD_UPDATE=1

ENTRYPOINT [ "/docker-entrypoint.sh" ]

CMD ["/usr/bin/supervisord", "-c", "/supervisord.conf"]
"""

def getTagsFromDockerhub(namespace, repo):
    headers = { "Accept": "application/json" }
    r = requests.get("https://hub.docker.com/v2/namespaces/%s/repositories/%s/tags?page_size=100" % (namespace, repo), headers=headers)
    result = r.json()
    tags = []
    for entry in result["results"]:
        if re.search("[0-9]+.[0-9]+.[0-9]+$", entry["name"]):
            tags.append(entry["name"])
    return tags

def getLatestNextcloudRelease():
    headers = { "Accept": "application/json" }
    r = requests.get("https://api.github.com/repos/nextcloud/server/tags", headers=headers)
    result = r.json()
    return result[0]["name"].replace("v", "")

def main():
    nextcloudTags = getTagsFromDockerhub("library", "nextcloud")
    netzintTags = getTagsFromDockerhub("netzint", "nextcloud-fpm")

    client = docker.from_env()
    r = client.login(username=os.getenv("DOCKERHUB_USERNAME"), password=os.getenv("DOCKERHUB_PASSWORD"))

    latestVersion = getLatestNextcloudRelease()

    for tag in nextcloudTags:
        if tag not in netzintTags:
            print("New nextcloud tag found '%s' and is ready to build!" % tag)
            with open("dockerfile.tmp", "w") as f:
                f.write(DOCKERFILE_TEMPLATE.replace("##TAG##", tag))
            try:
                print("  [%s] Start building docker image..." % tag, end="")
                client.images.build(dockerfile="dockerfile.tmp", tag="netzint/nextcloud-fpm:" + tag, path="./")
                print("  ok!")

            except:
                raise SystemExit("Error building image!")

            os.remove("dockerfile.tmp")

            try:
                print("  [%s] Start publishing docker image..." % tag, end="")
                client.images.push(repository="netzint/nextcloud-fpm", tag=tag)
                print("  ok!")
            except Exception as e:
                raise SystemExit("Error upload image! " + str(e))

            # check if this version is the latest release?
            if tag is latestVersion:
                try:
                    print("  [%s] This is the newest version of nextcloud. Publish as latest too!" % tag, end="")
                    client.images.push(repository="netzint/nextcloud-fpm", tag="latest")
                    print("  ok!")
                except Exception as e:
                    raise SystemExit("Error upload image! " + str(e))


if __name__ == "__main__":
    main()