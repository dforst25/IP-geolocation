import uvicorn
from fastapi import FastAPI
from routes import router
from storage import logger

app = FastAPI()

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the IP Geolocation Storage Service...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the IP Geolocation Storage Service...")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
