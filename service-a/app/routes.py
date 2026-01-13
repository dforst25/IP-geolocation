from fastapi import routing, HTTPException, Depends ,Query
from typing import Optional
from pydantic import IPvAnyAddress


from dependencies import get_logic_service
from services import LogicService

router = routing.APIRouter(prefix="/lookup_ip", tags=["IP Geolocation"])

@router.get("/", status_code=200)
async def get_ip_geo_point(ip: Optional[IPvAnyAddress] = Query(None)
                           ,logic_service: LogicService = Depends(get_logic_service)):
    
    ok, ip_loc = await logic_service.get_data_server_b(ip)

    if not ok:
        raise HTTPException(status_code=502, detail=f"Failed to get data from Service B: {ip_loc}")

    return ip_loc


@router.post("/", status_code=201)
async def post_ip_geo_point(ip: Optional[IPvAnyAddress] = Query(None)
                            , logic_service: LogicService = Depends(get_logic_service)):
    
    ok, response = await logic_service.process(ip)

    if not ok:
        raise HTTPException(status_code=502, detail=f"Failed to send data to Service B: {response}")

    return {"message": response}    
