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
 Version 1.2 from 2024/07/22 by Netzint GmbH
"""                                                                                  

def __execute(command):
    result = subprocess.run(command, stdout=PIPE, stderr=PIPE)
    if result.returncode != 0:
        print(f"Error executing command: {command}\n{result.stderr.decode()}")
    return result

def getNextcloudReleases():
    try:
        r = requests.get("https://download.nextcloud.com/server/releases/")
        r.raise_for_status()
        result = BeautifulSoup(r.text, 'html.parser')
        versions = [
            e.get("href").replace("nextcloud-", "").replace(".zip", "")
            for e in result.find_all('a')
            if e.get("href").startswith("nextcloud-") and e.get("href").endswith(".zip")
        ]
        return versions
    except requests.RequestException as e:
        print(f"Failed to get Nextcloud releases: {e}")
        return None

def getCurrentNextcloudVersion():
    try:
        r = requests.get("https://localhost/status.php", verify=False)
        r.raise_for_status()
        result = r.json()
        return result.get("versionstring")
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Failed to get current Nextcloud version: {e}")
        return None

def checkMaintenanceMode():
    try:
        r = requests.get("https://localhost/status.php", verify=False)
        r.raise_for_status()
        result = r.json()
        return result.get("maintenance", False)
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Failed to check maintenance mode: {e}")
        return False

def getLatestVersionFromCurrent(versions, current):
    try:
        major_version = current.split(".")[0]
        filter_res = [v for v in versions if v.split(".")[0] == major_version]

        if not filter_res:
            return None

        last_version_of_current = filter_res[-1]
        if last_version_of_current == current:
            next_major_version = str(int(major_version) + 1) + ".0.0"
            return getLatestVersionFromCurrent(versions, next_major_version)
        return last_version_of_current
    except Exception as e:
        print(f"Error determining latest version from current: {e}")
        return None

def update_docker_compose_override(version):
    try:
        with open("/srv/docker/nextcloud_docker_cluster/docker-compose.override.yml", "w") as f:
            f.write(f"""
version: '3.8'
services:
  app:
    image: netzint/nextcloud-fpm:{version}
  fpm01:
    image: netzint/nextcloud-fpm:{version}
  fpm02:
    image: netzint/nextcloud-fpm:{version}
  fpm03:
    image: netzint/nextcloud-fpm:{version}
  fpm04:
    image: netzint/nextcloud-fpm:{version}
            """)
    except IOError as e:
        print(f"Error writing docker-compose.override.yml: {e}")

def main():
    print(header)

    versions = getNextcloudReleases()
    if not versions:
        print("Failed to retrieve Nextcloud releases.")
        return

    current = getCurrentNextcloudVersion()
    if not current:
        print("Failed to retrieve current Nextcloud version.")
        return

    result = getLatestVersionFromCurrent(versions, current)

    if not result:
        print("🥳 You are already on the latest version! Congratulations 🥳🥳🥳")
        return

    print(f"⛏️ This script will update your Nextcloud from version {current} to version {result}. Do you want to continue with this version? (y/n)")

    while True:
        user_input = input("Type y to continue, n to specify a version manually, or q to cancel: ").strip().lower()

        if user_input == 'n':
            print("Please enter the version number you want to update to:")
            manual_version = input("Type the version number (e.g., 25.0.2): ").strip()

            if manual_version in versions:
                result = manual_version
                break
            else:
                print(f"❌ The version {manual_version} is not available. Please enter a valid version.")
        elif user_input == 'y':
            break
        elif user_input == 'q':
            print("As you wish... I cancel the update... 😥")
            return
        else:
            print("🫣 Really? Please type 'y', 'n', or 'q'.")

    print("Good choice 👍🏻")

    docker_compose_path = subprocess.run(['which', 'docker-compose'], stdout=PIPE, stderr=PIPE).stdout.decode().strip()
    if not docker_compose_path:
        print("Error: docker-compose not found.")
        return

    steps = [
        ("[STEP 1] Stopping the Nextcloud container...", ["/srv/docker/nextcloud_docker_cluster/daemonHandler.sh", "stop"]),
        ("[STEP 2] Overwriting the docker-compose.override.yml file...", lambda: update_docker_compose_override(result)),
        ("[STEP 3] Pulling new container from DockerHub...", [docker_compose_path, "--project-directory", "/srv/docker/nextcloud_docker_cluster/", "pull"]),
        ("[STEP 4] Starting the Nextcloud cluster...", ["/srv/docker/nextcloud_docker_cluster/daemonHandler.sh", "start"])
    ]

    for step_description, command in steps:
        print(step_description)
        if callable(command):
            command()
        else:
            __execute(command)

    print("Now sleeping 😴 for 20 seconds to wait for cluster to start...")
    for i in range(20):
        print(f"{20 - i} second(s) remaining...")
        time.sleep(1)

    print("Nextcloud should be up now... 💯 Sending update commands...")
    update_commands = [
        ["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "maintenance:mode", "--off"],
        ["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "upgrade"],
        ["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:add-missing-indices"],
        ["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:convert-filecache-bigint"],
        ["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:add-missing-primary-keys"],
        ["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "db:add-missing-columns"]
    ]

    if not checkMaintenanceMode():
        for cmd in update_commands:
            __execute(cmd)
    else:
        print("⚠️ Nextcloud seems to be in maintenance mode. Should I turn this off?")
        while True:
            user_input = input("Type y or n: ").strip().lower()
            if user_input == 'n':
                print("As you wish... I keep the maintenance mode on... 🙄")
                break
            elif user_input == 'y':
                __execute(["docker", "exec", "--user", "www-data", "-it", "nextcloud_docker_cluster_fpm01_1", "/var/www/html/occ", "maintenance:mode", "--off"])
                print("Maintenance mode is turned off 🫡")
                for cmd in update_commands:
                    __execute(cmd)
                break
            else:
                print("🫣 Really? Please type 'y' or 'n'.")

    print("Update finished 🧠! Happy working or if something went wrong, happy debugging!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
