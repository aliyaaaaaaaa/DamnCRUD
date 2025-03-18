#!/bin/bash
# entrypoint.sh
set -e

# Cek readiness MySQL
echo "Menunggu database siap..."
until mysqladmin ping -h db -u root -proot --silent; do
    echo "Database belum siap. Menunggu..."
    sleep 2
done
echo "Database sudah siap!"

# Jalankan PHP server di background
php -S 0.0.0.0:8000 -t /var/www/html &

# Tetap berjalan
tail -f /dev/null
