#!/bin/sh

exec python api.py --ws_subdomain "${WS_SUBDOMAIN:-wss.}" --account_email "${ACCOUNT_EMAIL:-demo@retrogile.com}" &
exec python ws.py --account_email "${ACCOUNT_EMAIL:-demo@retrogile.com}"
