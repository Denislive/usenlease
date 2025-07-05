#!/bin/sh

# ✅ Intercept Django management commands passed via ENTRYPOINT (commented out after admin creation)
# if echo "$@" | grep -q "manage.py"; then
#   echo "⚙️ Detected Django management command: $@"
#   cd /app/backend
#   exec python manage.py "${@#*manage.py }"
# fi

set -e  # Exit on any error

echo "🚀 Starting Backend Services..."

# Start Redis server first (Celery depends on it)
echo "📦 Starting Redis Server..."
redis-server --daemonize yes || { echo "❌ Failed to start Redis"; exit 1; }

echo "🧹 Removing old migrations..."
find /app/backend -path "*/migrations/*.py" -not -name "__init__.py" -delete
find /app/backend -path "*/migrations/*.pyc" -delete

# Make migrations
echo "🛠️ Creating new migrations..."
python /app/backend/manage.py makemigrations --noinput || {
    echo "❌ Makemigrations failed. Exiting."
    exit 1
}

# Apply migrations
echo "📦 Applying migrations..."
python /app/backend/manage.py migrate --noinput || {
    echo "⚠️ Migration failed, trying --fake..."
    python /app/backend/manage.py migrate --fake || {
        echo "❌ Fake migration also failed. Exiting."
        exit 1
    }
}

# Celery Beat migrations
echo "🔁 Applying Celery Beat migrations..."
python /app/backend/manage.py migrate django_celery_beat --noinput || {
    echo "⚠️ Celery Beat migration failed, continuing..."
}

echo "✅ Migrations completed successfully!"

# Collect static files
echo "🎨 Collecting static files..."
python /app/backend/manage.py collectstatic --noinput || {
    echo "❌ Static files collection failed"; exit 1;
}

# Start Gunicorn
echo "🔥 Starting Gunicorn on port 8000..."
cd /app/backend
gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:8000 --workers=2 --timeout 600 --graceful-timeout 600 &

# (Optional) Celery Worker & Beat — currently disabled
echo "Starting Celery Worker..."
celery -A EquipRentHub worker --loglevel=info &
echo "Starting Celery Beat..."
celery -A EquipRentHub beat --loglevel=info &

echo "🌍 Environment Variables:"
env

# Prepare Nginx config
export PORT=${PORT:-8080}

if [ -n "$PORT" ]; then
  echo "🛠️ Generating Nginx config from template..."
  envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
else
  echo "❌ PORT environment variable is not set. Exiting."
  exit 1
fi

echo "🧾 Substituted Nginx Config:"
cat /etc/nginx/nginx.conf

# Final Nginx config
echo "🧱 Creating final Nginx config..."
cat <<EOF > /etc/nginx/nginx.conf
worker_processes  auto;
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;

    client_body_buffer_size 50M;

    server {
        listen $PORT;
        server_name www.usenlease.com;
        return 301 https://usenlease.com\$request_uri;
    }
    server {
        listen ${PORT};  # Ensure this uses the dynamic PORT
        server_name usenlease.com;

        root /usr/share/nginx/html;

        client_max_body_size 20M;
        client_body_buffer_size 20M;

        proxy_read_timeout 600;
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        keepalive_timeout 600;

        location /admin {
            client_max_body_size 20M;
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            add_header 'Access-Control-Allow-Origin' 'https://usenlease.com' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Origin, Content-Type, Accept, Authorization' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
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

            add_header 'Access-Control-Allow-Origin' 'https://usenlease.com' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Origin, Content-Type, Accept, Authorization' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
        }

        location /static/ {
            alias /app/backend/staticfiles/;
        }

        location /media/ {
            alias /app/backend/media/;
        }

        error_page  500 502 503 504  /50x.html;
        location = /50x.html {
            root  /usr/share/nginx/html;
        }
    }
}
EOF

echo "🚦 Starting Nginx..."
nginx -g 'daemon off;' || { echo "❌ Failed to start Nginx"; exit 1; }
