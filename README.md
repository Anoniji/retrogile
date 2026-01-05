[![Pylint](https://github.com/Anoniji/retrogile/actions/workflows/pylint.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/pylint.yml)
[![Docker Image API](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-api.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-api.yml)
[![Docker Image WS](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-ws.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-ws.yml)
[![Docker Image Full](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-aio.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-aio.yml)
[![Python 3.14](https://img.shields.io/badge/python-3.14-green?style=square)](https://www.python.org/)

![alt text](https://github.com/Anoniji/retrogile/blob/main/img/favicon.png?raw=true)

# Retrogile
Agile Retrospective Management Tool

The version provided is currently in development and may have missing features or even operational issues.

## Demo
[Test server](https://www.retrogile.com)

## Dockerhub

- [FULL Image Page](https://hub.docker.com/r/anoniji/retrogile)

### Splitted services
- [API Image Page](https://hub.docker.com/r/anoniji/retrogile_api)
- [WS Image Page](https://hub.docker.com/r/anoniji/retrogile_ws)


## Podman Launch Example
```
podman run -d --restart=always -p "0.0.0.0:8008:8008" -v ./board:/mnt/retrogile/board -m=512m --cpus=1 -e WS_SUBDOMAIN="wss." --name retrogile_api retrogile_api
podman run -d --restart=always -p "0.0.0.0:8009:8009" -v ./board:/mnt/retrogile/board -m=512m --cpus=1 --name retrogile_ws retrogile_ws
podman run -d --restart=always -p "0.0.0.0:8008:8008" -p "0.0.0.0:8009:8009" -v ./board:/mnt/retrogile/board -m=512m --cpus=1 -e WS_SUBDOMAIN="wss." --name retrogile retrogile
```

**Variables available for Retrogile:**

| Variable | Description | Example |
|----------|-------------|---------|
| `WS_SUBDOMAIN` | WebSocket subdomain for connection | `-e WS_SUBDOMAIN="wss."` |
