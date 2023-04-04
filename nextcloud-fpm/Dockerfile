FROM nextcloud:26.0.0-fpm

RUN apt-get update && apt-get install -y \
    supervisor \
    smbclient \
    libsmbclient-dev \
    libgmp-dev \
    libicu-dev \
    sudo \
    libmagickcore-6.q16-3-extra \
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