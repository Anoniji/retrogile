#!/bin/sh

exec python api.py &
exec python ws.py --ws_subdomain "${WS_SUBDOMAIN:-wss.}"
