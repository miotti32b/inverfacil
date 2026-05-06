release: python manage.py migrate
web: python manage.py collectstatic --noinput && gunicorn mi_sitio_web.wsgi --worker-class gthread --workers 2 --threads 4 --timeout 120 --graceful-timeout 30 --keep-alive 5
