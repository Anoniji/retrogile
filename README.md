![alt text](https://github.com/Anoniji/retrogile/blob/main/img/favicon.png?raw=true)

[![Pylint](https://github.com/Anoniji/retrogile/actions/workflows/pylint.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/pylint.yml)
[![CodeQL](https://github.com/Anoniji/retrogile/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/github-code-scanning/codeql)
[![Docker Image Full](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-aio.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-aio.yml)
[![Python 3.14](https://img.shields.io/badge/python-3.14-green?style=square)](https://www.python.org/)

# Retrogile
Agile Retrospective Management Tool

The version provided is currently in development and may have missing features or even operational issues.

## Demo
[Test server](https://demo.retrogile.com)

## Dockerhub

- [FULL Image Page](https://hub.docker.com/r/anoniji/retrogile)

### Splitted services
- [API Image Page](https://hub.docker.com/r/anoniji/retrogile_api)
- [WS Image Page](https://hub.docker.com/r/anoniji/retrogile_ws)


## Podman Launch Example
```
podman run -d --restart=always -p "0.0.0.0:8008:8008" -v ./board:/mnt/retrogile/board -m=512m --cpus=1 -e WS_SUBDOMAIN="wss." -e DEBUG="False" --name retrogile retrogile
```

**Variables available for Retrogile:**

| Variable                     | Default | Description                                   | Example                                |
|------------------------------|---------|-----------------------------------------------|----------------------------------------|
| `DEBUG`                      | false   | Container debugging                           | `-e DEBUG="True/False"`                |
| `SERVICEHOST`                | 0.0.0.0 | Host address to bind the server to            | `-e SERVICEHOST="0.0.0.0"`             |
| `SERVICEPORT`                | 8008    | HTTP/WS port the server listens on            | `-e SERVICEPORT="8008"`                |
| `UVICORN_WORKERS`            | 1       | Number of worker processes for Uvicorn        | `-e UVICORN_WORKERS="4"`               |
| `UVICORN_LIMIT_CONCURRENCY`  | 1000    | Max concurrent connections per worker         | `-e UVICORN_LIMIT_CONCURRENCY="500"`   |
| `UVICORN_LIMIT_MAX_REQUESTS` | 10000   | Max requests per worker before worker restart | `-e UVICORN_LIMIT_MAX_REQUESTS="5000"` |
