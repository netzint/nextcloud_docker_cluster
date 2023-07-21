#!/usr/bin/env python3

import requests
import subprocess
import time

from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from subprocess import PIPE

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

header = """
  _   _ _____ _____ ________ _   _ _____                                             
 | \ | | ____|_   _|__  /_ _| \ | |_   _|                                            
 |  \| |  _|   | |   / / | ||  \| | | |                                              
 | |\  | |___  | |  / /_ | || |\  | | |                                              
 |_| \_|_____| |_| /____|___|_| \_| |_|                                              
  _   _           _       _                 _   _   _           _       _            
 | \ | | _____  _| |_ ___| | ___  _   _  __| | | | | |_ __   __| | __ _| |_ ___ _ __ 
 |  \| |/ _ \ \/ / __/ __| |/ _ \| | | |/ _` | | | | | '_ \ / _` |/ _` | __/ _ \ '__|
 | |\  |  __/>  <| || (__| | (_) | |_| | (_| | | |_| | |_) | (_| | (_| | ||  __/ |   
 |_| \_|\___/_/\_\\__\___|_|\___/ \__,_|\__,_|  \___/| .__/ \__,_|\__,_|\__\___|_|   
                                                     |_|                             
 __     __  _           ____   ___ ____  _____      __   ___ _____      __  ____  _  
 \ \   / / / |         |___ \ / _ \___ \|___ /     / /  / _ \___  |    / / |___ \/ | 
  \ \ / /  | |  _____    __) | | | |__) | |_ \    / /  | | | | / /    / /    __) | | 
   \ V /   | | |_____|  / __/| |_| / __/ ___) |  / /   | |_| |/ /    / /    / __/| | 
    \_/    |_|         |_____|\___/_____|____/  /_/     \___//_/    /_/    |_____|_| 
                                                                                     
"""                                                                                  

def __execute(command):
    return subprocess.run(command, stdout=PIPE, stderr=PIPE)

def getNextcloudReleases():
    try:
        r = requests.get("https://download.nextcloud.com/server/releases/")
        result = r.text
        result = BeautifulSoup(result, 'html.parser')
        versions = []
        for e in result.find_all('a'):
            v = e.get("href")
            if v.startswith("nextcloud-") and v.endswith(".zip"):
                versions.append(v.replace("nextcloud-", "").replace(".zip", ""))
        return versions
    except:
        return None

def getCurrentNextcloudVersion():
    try:
        r = requests.get("https://localhost/status.php", verify=False)
        result = r.json()
        return result["versionstring"]
    except:
        return None

def checkMaintenanceMode():
    try:
        r = requests.get("https://localhost/status.php", verify=False)
        result = r.json()
        return result["maintenance"]
    except:
        return False

def getLatestVersionFromCurrent(versions, current):
    result = []
    for version in versions:
        if current.split(".")[0] + "." + current.split(".")[1] in version:
            result.append(version)
    if result[len(result) - 1] in current:
        return getLatestVersionFromCurrent(versions, str(int(current.split(".")[0]) + 1) + ".0.0")
    return result[len(result) - 1]

def main():
    versions = getNextcloudReleases()
    current = getCurrentNextcloudVersion()
    result = getLatestVersionFromCurrent(versions, current)
    
    print(header)
    print("⛏️ This script update your nextcloud from version %s to version %s. Do you want to continue? (y/n)" % (current, result))
    while True:
        user = input("Type y or n: ")
        if "n" in user:
            print("As you wish... I cancel the update... 😥")
            exit()
        elif "y" in user:
            break
        else:
            print("🫣 Really?")

    print()
    print("Good choice 👍🏻")
    print("[STEP 1] Now I'm stopping the Nextcloud container...")
    __execute(["/srv/docker/nextcloud_docker_cluster/daemonHandler.sh",  "stop"])

    print("[STEP 2] Overwriting the docker-compose.override.yml file...")
    with open("/srv/docker/nextcloud_docker_cluster/docker-compose.override.yml", "w") as f:
        f.write("""version: '3.8'
services:
  app:
    image: netzint/nextcloud-fpm:#version#
  fpm01:
    image: netzint/nextcloud-fpm:#version#
  fpm02:
    image: netzint/nextcloud-fpm:#version#
  fpm03:
    image: netzint/nextcloud-fpm:#version#
  fpm04:
    image: netzint/nextcloud-fpm:#version#
        """.replace("#version#", result))
    
    print("[STEP 3] Pulling new container from dockerhub...")
    __execute(["/usr/local/bin/docker-compose",  "--project-directory", "/srv/docker/nextcloud_docker_cluster/", "pull"])

    print("[STEP 4] Starting the nextcloud cluster...")
    __execute(["/srv/docker/nextcloud_docker_cluster/daemonHandler.sh",  "start"])

    print()
    print("Now sleeping 😴 for 20 seconds to wait for cluster to start...")
    for i in range(0, 20):
        print("%i second(s) remaining..." % (20 - i))
        time.sleep(1)

    print()
    print("Nextcloud should be up now... 💯 Try to send update commands....")
    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "maintenance:mode", "--off"])
    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "upgrade"])
    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:add-missing-indices"])
    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:convert-filecache-bigint"])
    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:add-missing-primary-keys"])
    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:add-missing-columns"])
    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "app:update", "--all"])

    check = getCurrentNextcloudVersion()
    if check is not None and result in check:
        print("✅ Nextcloud %s is up and running!" % check)
        if checkMaintenanceMode():
            print()
            print("⚠️ Nextcloud seems to be in maintenance mode. Should I turn this off?")
            while True:
                user = input("Type y or n: ")
                print()
                if "n" in user:
                    print("As you wish... I keep the maintanance mode on... 🙄")
                    break
                elif "y" in user:
                    __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "maintenance:mode", "--off"])
                    print("Maintenance mode is turned off 🫡")
                    break
                else:
                    print("🫣 Really?")

    else:
        print("❌ Something went wrong... Please check if containers are up and running...")

    print()
    print("Update finished 🧠! Happy working or if something went wrong, happy debugging!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass