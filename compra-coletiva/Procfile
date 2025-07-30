web: gunicorn projeto_compra_coletiva.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A projeto_compra_coletiva worker -l info
beat: celery -A projeto_compra_coletiva beat -l info --pidfile=/tmp/celerybeat.pid