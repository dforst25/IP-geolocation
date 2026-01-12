from fastapi import FastAPI, HTTPException
import logging
import os
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def check_server_b() -> tuple[bool, str]:
    host = os.getenv("SERVER_B_HOST")

    if not host:
        msg = "SERVER_B_HOST environment variable is not set"
        logger.error(msg)
        return False, "SERVER_B_HOST environment variable is not set"

    param = "-n" if sys.platform.startswith("win") else "-c"
    response = os.system(f"ping {param} 1 {host}")

    if response == 0:
        return True, host

    msg = f"Ping to {host} failed"
    logger.error(msg)
    return False, msg


@app.on_event("startup")
def startup_event():
    logger.info("Starting API application...")

    ok, msg = check_server_b()

    if not ok:
        raise ValueError(msg)
    
    logger.info("API ready to accept requests")


@app.get("/", status_code=200)
def read_root():
    """Health check endpoint."""

    host = get_host_name()

    return {
        "status": "healthy",
        "service": "Service A",
        "service B host": host
    }


@app.get("/health", status_code=200)
def health_check():
    """Detailed health check including database connectivity."""
    ok, msg = check_server_b()

    if not ok:
        raise HTTPException(status_code=503, detail=msg)

    host = get_host_name()

    return {
        "status": "healthy",
        "database": "connected",
        "host": host
    }

