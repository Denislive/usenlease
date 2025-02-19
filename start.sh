#!/bin/sh

set -e  # Exit on any error

echo "Starting Backend..."

# Activate virtual environment or create it if it doesn't exist
if [ ! -d "/app/backend/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv /app/backend/venv
fi
source /app/backend/venv/bin/activate

# Install dependencies inside the virtual environment
pip install --no-cache-dir --break-system-packages -r /app/backend/requirements.txt || {
    echo "Failed to install dependencies"
    exit 1
}

# Run database migrations
echo "Running database migrations..."
python /app/backend/manage.py makemigrations --noinput || {
    echo "Makemigrations failed"
    exit 1
}
python /app/backend/manage.py migrate --noinput || {
    echo "Migrating failed"
    exit 1
}

# Collect static files
echo "Collecting static files..."
python /app/backend/manage.py collectstatic --noinput || {
    echo "Static files collection failed"
    exit 1
}

# Start Gunicorn server for the Django backend
export PORT=${PORT:-8080}
echo "Starting Gunicorn server on port 8000..."
cd /app/backend
exec gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:8000 --workers=3 --timeout 240 --graceful-timeout 240 &

# Ensure Nginx uses the correct port dynamically
echo "Creating Nginx config template..."
cat <<EOF > /etc/nginx/nginx.template.conf
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_body_buffer_size 30M;

    include /etc/nginx/conf.d/*.conf;

    server {
        listen \$PORT;
        server_name www.usenlease.com;
        return 301 https://usenlease.com\$request_uri;
    }

    server {
        listen \$PORT;
        server_name usenlease.com;

        root /usr/share/nginx/html;

        location /admin {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            add_header 'Access-Control-Allow-Origin' 'https://usenlease.com';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Origin, Content-Type, Accept, Authorization';
        }

        location / {
            try_files \$uri \$uri/ /index.html;
        }

        location /api {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            add_header 'Access-Control-Allow-Origin' 'https://usenlease.com';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Origin, Content-Type, Accept, Authorization';
        }

        location /static/ {
            alias /app/backend/staticfiles/;
        }

        location /media/ {
            alias /app/backend/media/;
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
EOF

# Use envsubst to replace \$PORT dynamically
envsubst '\$PORT' < /etc/nginx/nginx.template.conf > /etc/nginx/nginx.conf

# Log the final configuration for verification
echo "Final Nginx Config:"
cat /etc/nginx/nginx.conf

# Start Nginx
echo "Starting Nginx..."
exec nginx -g 'daemon off;'
