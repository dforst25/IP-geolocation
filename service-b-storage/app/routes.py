from fastapi import APIRouter, HTTPException
from schemas import IpGeoPoint, GeoPoint
from storage import *

router = APIRouter()


@router.post("/ip-geopoint/", status_code=201)
async def create_ip_geopoint(ip_geo_point: IpGeoPoint):
    store_ip_geopoint(ip_geo_point)
    return ip_geo_point.model_dump()


@router.get("/ip-geopoint/")
async def get_ip_geopoint(ip: str):
    geo_point = retrieve_ip_geopoint(ip)
    if geo_point is None:
        raise HTTPException(status_code=404, detail="GeoPoint not found for the given IP")
    return geo_point.model_dump()


@router.delete("/ip-geopoint/{ip}", status_code=204)
async def delete_ip_geopoint_api(ip: str):
    delete_ip_geopoint(ip)
    return None


@router.get("/healthcheck/", status_code=200)
async def healthcheck():
    return {"status": "ok"}


@router.get("/")
async def root():
    return {"message": "Welcome to the IP Geolocation Storage Service!"}


@router.get("/all-ip-geopoints/")
async def get_all_ip_geopoints_api():
    """Retrieve all stored IP and GeoPoint pairs from Redis."""
    ip_geopoints = get_all_ip_geopoints()
    return [ip_geo_point.model_dump() for ip_geo_point in ip_geopoints]


@router.put("/ip-geopoint/", status_code=200)
async def update_ip_geopoint_api(ip_geo_point: IpGeoPoint):
    """Update the GeoPoint for a given IP in Redis."""
    update_ip_geopoint(ip_geo_point)
    return ip_geo_point.model_dump()


@router.delete("/clear-all/", status_code=204)
async def clear_all_data_api():
    """Clear all data from the Redis database."""
    clear_all_data()
    return None
