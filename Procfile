web: sh -c "cd backend && python manage.py wait_for_db && python manage.py migrate && python manage.py create_superuser && gunicorn EquipRentHub.wsgi:application --bind 0.0.0.0:$PORT --workers=3 --timeout 240 --graceful-timeout 240"
frontend: sh -c "cd frontend && serve -s dist -l $PORT"
