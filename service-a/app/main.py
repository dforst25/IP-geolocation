from fastapi import FastAPI, HTTPException, Depends
import logging


from logging_config import setup_logging
from services import CommunicationService
from dependencies import get_communication_service

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
def startup_event(communication_service: CommunicationService = 
                  Depends(get_communication_service)):
    
    logger.info("Starting API application...")

    ok, msg = communication_service.check_server_b()

    if not ok:
        raise ValueError(msg)
    
    logger.info("API ready to accept requests")


@app.get("/", status_code=200)
def read_root(communication_service: CommunicationService = 
              Depends(get_communication_service)):
    
    """Health check endpoint."""

    host = communication_service.server_b_host

    return {
        "status": "healthy",
        "service": "Service A",
        "service B host": host
    }


@app.get("/health", status_code=200)
def health_check(communication_service: CommunicationService = 
                  Depends(get_communication_service)):

    ok, msg = communication_service.check_server_b()

    if not ok:
        raise HTTPException(status_code=503, detail=msg)

    host = communication_service.server_b_host

    return {
        "status": "healthy",
        "database": "connected",
        "host": host
    }

