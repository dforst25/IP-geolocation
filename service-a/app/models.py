from pydantic import BaseModel, field_validator


class Ip(BaseModel):
    ip :str

@field_validator('ip', mode='before')
def validate_ip(cls, v):
    parts = v.split('.')
    if len(parts) != 4 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
        raise ValueError("Invalid IP address format")
    return v

class IpLocation(Ip):
    lat: float
    lon: float

