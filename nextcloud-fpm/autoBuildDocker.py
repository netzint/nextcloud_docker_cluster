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
    try: 
        headers = { "Accept": "application/json" }
        r = requests.get("https://api.github.com/repos/nextcloud/server/tags", headers=headers)
        result = r.json()
        for res in result:
            if "rc" not in res["name"] and "beta" not in res["name"]:
                return res["name"].replace("v", "")
        return None
    except:
        return None

def buildImage(tag, client, name=None):
    with open("dockerfile.tmp", "w") as f:
        f.write(DOCKERFILE_TEMPLATE.replace("##TAG##", tag))

    if not name:
        name = tag

    try:
        print("  [%s] Start building docker image..." % name, end="")
        res = client.images.build(dockerfile="dockerfile.tmp", tag="netzint/nextcloud-fpm:" + name, path="./")
        print("  ok!")
    except Exception as e:
        raise SystemExit("Error building image! " + str(e))

    os.remove("dockerfile.tmp")
    return res

def publishImage(tag, client, name=None):
    if not name:
        name = tag

    try:
        print("  [%s] Start publishing docker image..." % name, end="")
        res = client.images.push(repository="netzint/nextcloud-fpm", tag=name)
        print("  ok!")
    except Exception as e:
        raise SystemExit("Error upload image! " + str(e))

    return res

def main():
    nextcloudTags = getTagsFromDockerhub("library", "nextcloud")
    netzintTags = getTagsFromDockerhub("netzint", "nextcloud-fpm")

    client = docker.from_env()
    client.login(username=os.getenv("DOCKERHUB_USERNAME"), password=os.getenv("DOCKERHUB_PASSWORD"))

    latestVersion = getLatestNextcloudRelease()

    for tag in nextcloudTags:
        if tag not in netzintTags:
            print("New nextcloud tag found '%s' and is ready to build!" % tag)
            res_build = buildImage(tag, client)
            print("Build-Result: " + str(res_build))
            res_pub = publishImage(tag, client)
            print("Publish-Result: " + str(res_pub))

            # check if this version is the latest release?
            if latestVersion is not None and tag in latestVersion:
                buildImage(tag, client, "latest")
                publishImage(tag, client, "latest")

                with open("../build-infos-header.txt", "w") as f:
                    f.write("Release v%s" % tag)
                with open("../build-infos-tag.txt", "w") as f:
                    f.write(tag)
                with open("../build-infos-body.txt", "w") as f:
                    f.write("Version %s has just been built as a Docker container. This version is the most current on Nextcloud and has therefore been marked as 'latest'." % tag)

    with open("../build-infos-info.txt", "w") as f:
        f.write("Run finished!")


if __name__ == "__main__":
    main()
