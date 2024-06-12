run the server: gunicorn core.asgi:application -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
