web: gunicorn docdisplay.wsgi:application --timeout 120
worker: python manage.py qcluster
release: python manage.py migrate --noinput && python manage.py search_index --create