python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input
cp -r /app/backend_static/. /backend_static/static/
python manage.py import_json
gunicorn --bind 0.0.0.0:8000 backend.wsgi