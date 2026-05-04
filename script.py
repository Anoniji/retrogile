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

# ///////////////////////////////////////////////////////////////////////
# IMPORTS CRITIQUES
# ///////////////////////////////////////////////////////////////////////

from libs.api import app as flask_app, init_api
from libs.ws import ws_endpoint, init_ws

# ///////////////////////////////////////////////////////////////////////
# INITIALISATION GLOBALE (au niveau MODULE)
# ///////////////////////////////////////////////////////////////////////

# Initialise API et WS **UNE FOIS** au chargement du module
init_api()
init_ws()

# Wrapper Flask → ASGI (HTTP SEULEMENT)
api_asgi = WsgiToAsgi(flask_app)

# ///////////////////////////////////////////////////////////////////////
# APPLICATION PRINCIPALE ASGI
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
# CONFIGURATION LOGGING
# ///////////////////////////////////////////////////////////////////////


def setup_logging(debug: bool = False):
    """Configure logging selon mode."""
    if debug:
        # Console colorée
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)8s] %(name)-12s: %(message)s",
            datefmt="%H:%M:%S"
        )
    else:
        # Fichier rotation
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
# POINT D'ENTRÉE PRINCIPAL
# ///////////////////////////////////////////////////////////////////////


def main():
    """Lance le serveur."""
    # Parse env
    debug = os.getenv("DEBUG", "false").lower() == "true"
    port = int(os.getenv("SERVICEPORT", "8008"))

    # Logging
    setup_logging(debug)
    logger = logging.getLogger("retrogile.main")

    # Status
    logger.info("=" * 60)
    logger.info(f"   Debug:  {debug}")
    logger.info(f"   Port:   {port}")
    logger.info(f"   HTTP:   http://0.0.0.0:{port}")
    logger.info(f"   WS:     ws://0.0.0.0:{port}/ws")
    logger.info("=" * 60)

    # uvicorn → "script:app" (app GLOBALE)
    uvicorn.run(
        "script:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="debug" if debug else "info",
        access_log=debug,
        workers=1,
        limit_concurrency=1000,
        limit_max_requests=10000
    )

if __name__ == "__main__":
    main()
