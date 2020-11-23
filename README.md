Introduction
============

Nextcloud

Changelog

  # 2020.11.06
    - Initial


Static Content
===============

ni-nextcloud-fpm is build by us and contains the neccessary addons we need for ldap and samba access.

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



How it works
============

First run the init.sh. This file creates the first mariadb container and adds the neccessary nextcloud database structure.

Afterwards run docker-compose up and wait until the databases are in sync.

Once this happens stop the process by hitting ctrl + c

Now open db01-data/grastate.dat and set the bootstrap value from 0 to 1.

Now run startCluster.sh, wait a few seconds and run postinst.sh.

Postinst.sh adds the last missing database indicies and configures nextcloud to use cron instead of ajax.

Now log in via webinterface and create the administrator account.


