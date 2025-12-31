#!/bin/sh

echo " * WS_SUBDOMAIN: ${WS_SUBDOMAIN:-wss.}"
exec python api.py &
exec python ws.py --ws_subdomain "${WS_SUBDOMAIN:-wss.}"
