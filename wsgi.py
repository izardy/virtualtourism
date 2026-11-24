"""Production entry point (gunicorn wsgi:app). app.py is for local `python app.py`;
it cannot be imported by gunicorn because the package app/ has the same name."""
from app import create_app

app = create_app()
