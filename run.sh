#!/bin/sh

exec python api.py --ws_subdomain "${WS_SUBDOMAIN:-wss.}" &
exec python ws.py
