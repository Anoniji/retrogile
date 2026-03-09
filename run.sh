#!/bin/sh

exec python api.py --ws_subdomain $WS_SUBDOMAIN --debug $DEBUG &
exec python ws.py --debug $DEBUG
