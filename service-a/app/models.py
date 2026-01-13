from pydantic import BaseModel, IPvAnyAddress


class IpLocation(BaseModel):
    ip: str
    geo_point: dict[str, float]

