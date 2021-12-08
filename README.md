Introduction
============

Nextcloud

Changelog

  # 2020.11.06
    - Initial


Static Content
===============

ni-nextcloud-fpm is build by us and contains the neccessary addons we need for ldap and samba access.


Update existing installations
=============================

To update your existing installation, do the following steps:
- pull the new changes from github
- run updatescript
- if error occours this would be a problem....

Environment Variables
=====================

Environment Variables can be set in db.env. These contain the neccessary Data for database connections


- `MYSQL_ROOT_PASSWORD=test123`
- `MYSQL_PASSWORD=Muster`
- `MYSQL_DATABASE=nextcloud`
- `MYSQL_USER=nextcloud`
- `MYSQL_HOST=nc-sqlbroker`
- `REDIS_HOST=redis01`
- `REDIS_HOST_PASSWORD=redis2020passwordImportant`
- `TRUSTED_PROXIES=174.24.0.4`
- `NEXTCLOUD_ADMIN=admin`
- `NEXTCLOUD_ADMIN_PASSWORD=Muster!`
- `INTERNAL_IP=10.10.1.134`
- `INTERNAL_DOMAINNAME=nextcloud.netzint.de`

How it works
============

First run the init.sh. This file creates the first mariadb container and adds the neccessary nextcloud database structure. Afterwards
it spawns the second db and configures the grafana mariadb features and enables the safe_to_bootstrap value for db01, copys the default
configs from the template directory and hints to enable the systemd service.

You can then run the cluster via systemd or the daemonHandler.sh script (start / stop)

Once the Nextcloud is up and running run the postInst.sh do run the Nextcloud setup process (generate admin, enable apps etc.)

.


