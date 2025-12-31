#!/bin/sh

WS_SUBDOMAIN="wss."
while [ $# -gt 0 ]; do
  case "$1" in
    --ws_subdomain)
      WS_SUBDOMAIN="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

echo "WS_SUBDOMAIN: $WS_SUBDOMAIN"
exec python api.py &
exec python ws.py --ws_subdomain "$WS_SUBDOMAIN"
