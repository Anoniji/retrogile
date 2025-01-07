[![Pylint](https://github.com/Anoniji/retrogile/actions/workflows/pylint.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/pylint.yml)
[![Docker Image API](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-api.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-api.yml)
[![Docker Image WS](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-ws.yml/badge.svg)](https://github.com/Anoniji/retrogile/actions/workflows/docker-image-ws.yml)

![alt text](https://github.com/Anoniji/retrogile/blob/main/img/icone.png?raw=true)

# Retrogile
Agile Retrospective Management Tool

The version provided is currently in development and may have missing features or even operational issues.

## Demo (v0.2.7)
[Test server](https://retrogile.anoniji.dev)

## Dockerhub
- [API Image Page](https://hub.docker.com/repository/docker/anoniji/retrogile_api/general)
- [WS Image Page](https://hub.docker.com/repository/docker/anoniji/retrogile_ws/general)

## Podman Launch Example
```
podman run -d --restart=always -p "0.0.0.0:8008:8008" -v ./board:/mnt/retrogile/board -m=512m --cpus=1 --name retrogile_api retrogile_api
podman run -d --restart=always -p "0.0.0.0:8009:8009" -v ./board:/mnt/retrogile/board -m=512m --cpus=1 --name retrogile_ws retrogile_ws
```
