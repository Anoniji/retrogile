#!/bin/sh

exec python api.py --ws_subdomain "${WS_SUBDOMAIN:-wss.}" --account_email "${ACCOUNT_EMAIL}" &
exec python ws.py
