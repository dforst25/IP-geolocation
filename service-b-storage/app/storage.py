import redis
from schemas import IpGeoPoint, GeoPoint
import os
import time
import logging

logger = logging.getLogger(__name__)


def get_redis_connection():
    """Create a Redis connection using environment variables."""
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD", "0000"),
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            r.ping()
            logger.info(f"Successfully connected to Redis at {os.getenv('REDIS_HOST')}")
            return r
        except redis.ConnectionError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Redis connection attempt {attempt + 1} failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to Redis after {max_retries} attempts")
                raise


def store_ip_geopoint(ip_geo_point: IpGeoPoint) -> None:
    """Store an IP and its corresponding GeoPoint in Redis."""
    redis_conn = get_redis_connection()
    key = ip_geo_point.ip
    value = f"{ip_geo_point.geo_point.lat}, {ip_geo_point.geo_point.lon}"
    redis_conn.set(key, value)
    logger.info(f"Stored GeoPoint for IP {ip_geo_point.ip} in Redis.")


def retrieve_ip_geopoint(ip: str) -> GeoPoint | None:
    """Retrieve the GeoPoint for a given IP from Redis."""
    redis_conn = get_redis_connection()
    value = redis_conn.get(ip)
    if value:
        lat_str, lon_str = value.split(", ")
        geo_point = GeoPoint(lat=float(lat_str), lon=float(lon_str))
        logger.info(f"Retrieved GeoPoint for IP {ip} from Redis.")
        return geo_point
    else:
        logger.info(f"No GeoPoint found for IP {ip} in Redis.")
        return None


def delete_ip_geopoint(ip: str) -> None:
    """Delete the GeoPoint for a given IP from Redis."""
    redis_conn = get_redis_connection()
    redis_conn.delete(ip)
    logger.info(f"Deleted GeoPoint for IP {ip} from Redis.")


def update_ip_geopoint(ip_geo_point: IpGeoPoint) -> None:
    """Update the GeoPoint for a given IP in Redis."""
    redis_conn = get_redis_connection()
    key = ip_geo_point.ip
    value = f"{ip_geo_point.geo_point.lat}, {ip_geo_point.geo_point.lon}"
    redis_conn.set(key, value)
    logger.info(f"Updated GeoPoint for IP {ip_geo_point.ip} in Redis.")


def clear_all_data() -> None:
    """Clear all data from the Redis database."""
    redis_conn = get_redis_connection()
    redis_conn.flushdb()
    logger.info("Cleared all data from Redis database.")

def get_all_ip_geopoints() -> list[IpGeoPoint]:
    """Retrieve all stored IP and GeoPoint pairs from Redis."""
    redis_conn = get_redis_connection()
    keys = redis_conn.keys()
    result = []
    for key in keys:
        value = redis_conn.get(key)
        lat_str, lon_str = value.split(", ")
        geo_point = GeoPoint(lat=float(lat_str), lon=float(lon_str))
        result.append(IpGeoPoint(ip=key, geo_point=geo_point))
    logger.info("Retrieved all IP and GeoPoint pairs from Redis.")
    return result
