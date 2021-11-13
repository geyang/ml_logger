# Setting Up Dash Server



```bash
openssl genrsa 2048 > host.key
chmod 400 host.key
openssl req -new -x509 -nodes -sha256 -days 365 -key host.key -out host.cert
```





To Launch the Server



```bash
SANIC_REQUEST_MAX_SIZE=5000000000 SANIC_REQUEST_TIMEOUT=3600 SANIC_RESPONSE_TIMEOUT=3600 screen -dm python -m ml_logger.server --logdir ~/runs --port 8080 --host 0.0.0.0 --workers 16
```

