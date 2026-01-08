#!/bin/sh

exec python api.py --ws_subdomain $WS_SUBDOMAIN --account_email $ACCOUNT_EMAIL &
exec python ws.py --account_email $ACCOUNT_EMAIL
