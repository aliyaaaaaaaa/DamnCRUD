#!/bin/bash
# entrypoint.sh

# Jalankan PHP server di background
php -S 0.0.0.0:8000 -t /var/www/html &

# Tetap berjalan
tail -f /dev/null
