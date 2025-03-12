# Gunakan image PHP dengan Apache
FROM php:8.2-apache

# Set working directory
WORKDIR /var/www/html

# Salin semua file proyek ke dalam container
COPY . .

# Berikan izin yang diperlukan
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Aktifkan module yang diperlukan (jika ada)
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Expose port 80 untuk akses web
EXPOSE 80

# Jalankan Apache
CMD ["apache2-foreground"]
