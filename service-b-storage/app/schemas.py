from pydantic import BaseModel, Field, field_validator, IPvAnyAddress

IP_PATTERN = {
    "base_10": r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    }


class GeoPoint(BaseModel):
    lat: float
    lon: float


class IpGeoPoint(BaseModel):
    ip: str
    geo_point: GeoPoint


@field_validator("lat", mode="before")
def validate_coordinates(cls, v: float) -> float:
    if not -90 <= v <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    return v


@field_validator("lon", mode="before")
def validate_lon(cls, v: float) -> float:
    if not -180 <= v <= 180:
        raise ValueError("Longitude must be between -180 and 180")
    return v


@field_validator("ip", mode="before")
def validate_ip(cls, v: str) -> str:
    import re

    if not any(re.match(pattern, v) for pattern in IP_PATTERN.values()):
        raise ValueError("Invalid IP address format")
    return v
