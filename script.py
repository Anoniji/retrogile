#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script Name: Retrogile API
Author: Niji Ano
Date: 2026-05-04

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007
"""

import os
import sys
import logging
import uvicorn

from starlette.applications import Starlette
from starlette.routing import Mount, WebSocketRoute
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware
from asgiref.wsgi import WsgiToAsgi

from libs.api import app as flask_app, init_api
from libs.ws import ws_endpoint, init_ws


# ///////////////////////////////////////////////////////////////////////


init_api()
init_ws()
api_asgi = WsgiToAsgi(flask_app)


# ///////////////////////////////////////////////////////////////////////


app = Starlette(
    routes=[
        WebSocketRoute("/ws", endpoint=ws_endpoint),
        Mount("/", app=api_asgi),
    ],
    middleware=[
        Middleware(GZipMiddleware, minimum_size=1000),
    ]
)


# ///////////////////////////////////////////////////////////////////////


def setup_logging(debug: bool = False):
    """Configure application-wide logging.

    If debug is True, logging is set to DEBUG level with colored console output
    and a simplified time format. Otherwise, logging is set to INFO level with
    messages written both to stdout and to a rotating log file located in the
    .logs directory.

    Args:
        debug (bool): Enables verbose debug logging when True.
    """
    if debug:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)8s] %(name)-12s: %(message)s",
            datefmt="%H:%M:%S"
        )
    else:
        os.makedirs(".logs", exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)8s] %(name)-12s: %(message)s",
            handlers=[
                logging.FileHandler(".logs/retrogile.log"),
                logging.StreamHandler(sys.stdout)
            ],
            datefmt="%Y-%m-%d %H:%M:%S"
        )


# ///////////////////////////////////////////////////////////////////////


def main():
    """Start the Retrogile web server.

    Reads configuration from environment variables:
        DEBUG: enable debug mode and verbose logging (default: "false")
        SERVICEHOST: host address to bind the server to (default: "0.0.0.0")
        SERVICEPORT: HTTP/WS port to bind to (default: 8008)
        UVICORN_WORKERS: number of worker processes (default: 1)
        UVICORN_LIMIT_CONCURRENCY: max concurrent connections per worker (default: 1000)
        UVICORN_LIMIT_MAX_REQUESTS: max requests per worker before restart (default: 10000)

    Logs startup info (debug flag, port, HTTP and WS URLs) and then runs the Uvicorn
    server with the "script:app" ASGI application on 0.0.0.0, using the values above.
    In debug mode, Uvicorn enables reload and debug-level logging and access logs.
    """

    # Parse env
    debug = os.getenv("DEBUG", "false").lower() == "true"
    host = os.getenv("SERVICEHOST", "0.0.0.0")
    port = int(os.getenv("SERVICEPORT", "8008"))
    workers = int(os.getenv("UVICORN_WORKERS", "1"))
    limit_concurrency = int(os.getenv("UVICORN_LIMIT_CONCURRENCY", "1000"))
    limit_max_requests = int(os.getenv("UVICORN_LIMIT_MAX_REQUESTS", "10000"))

    setup_logging(debug)
    logger = logging.getLogger("retrogile.main")
    logger.info("=" * 60)
    logger.info(f"  Debug: {debug}")
    logger.info(f"  Port : {port}")
    logger.info(f"  HTTP : http://{host}:{port}")
    logger.info(f"  WS   : ws://{host}:{port}/ws")
    logger.info("=" * 60)

    uvicorn.run(
        "script:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info",
        access_log=debug,
        workers=workers,
        limit_concurrency=limit_concurrency,
        limit_max_requests=limit_max_requests,
    )

if __name__ == "__main__":
    main()
