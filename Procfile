release: python manage.py migrate
web: gunicorn base.wsgi --chdir base --log-file - --bind 0.0.0.0:$PORT