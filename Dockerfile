FROM php:8.0-apache
WORKDIR /var/www/html

RUN apt-get update && \
    docker-php-ext-install mysqli pdo_mysql && \
    docker-php-ext-enable mysqli pdo_mysql

COPY ./ ./
EXPOSE 80