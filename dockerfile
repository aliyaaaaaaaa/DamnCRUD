# Gunakan image PHP dengan Apache
FROM php:7.4-cli

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY . .

RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zip \
    unzip \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd mysqli pdo pdo_mysql

# Install MySQL Client
RUN apt-get update && apt-get install -y default-mysql-client

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ekspos port 8000
EXPOSE 8000

CMD ["/entrypoint.sh"]
