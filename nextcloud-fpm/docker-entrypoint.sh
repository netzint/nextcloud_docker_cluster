#!/bin/bash

if [[ -z "${NEXTCLOUD_ENABLE_CRON}" ]]; then
    NEXTCLOUD_ENABLE_CRON="1"
fi

if [[ "${NEXTCLOUD_ENABLE_CRON}" == "0" ]]; then
    cat <<EOF > /supervisord.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisord/supervisord.log
pidfile=/var/run/supervisord/supervisord.pid
childlogdir=/var/log/supervisord/
logfile_maxbytes=50MB
logfile_backups=10
loglevel=error

[program:php-fpm]
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
command=php-fpm
EOF

    echo '' > /var/spool/cron/crontabs/www-data

else
    cat <<EOF > /supervisord.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisord/supervisord.log
pidfile=/var/run/supervisord/supervisord.pid
childlogdir=/var/log/supervisord/
logfile_maxbytes=50MB
logfile_backups=10
loglevel=error

[program:php-fpm]
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
command=php-fpm

[program:cron]
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
command=/cron.sh
EOF

fi

/entrypoint.sh $@