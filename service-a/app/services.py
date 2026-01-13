import logging
from typing import Callable, Optional, Awaitable
from pydantic import IPvAnyAddress

from utils import safe_request, Response
from models import IpLocation


IP_LOC_URL = "http://ip-api.com/json/{}"

logger = logging.getLogger(__name__)

class CommunicationService:
    
    def __init__(self, server_b_host, server_b_port='', timeout=10):


        self.__server_b_host = 'http://' +server_b_host

        if server_b_port:

            self.__server_b_host += (':' + server_b_port)
        self.__timeout = timeout

    @property
    def server_b_host(self):
        return self.__server_b_host


    async def check_server_b(self) -> tuple[bool, str]:

        if not self.server_b_host:
            msg = "SERVER_B_URL environment variable is not set"
            logger.error(msg)
            return False, msg

     
        r: Response = await safe_request(method='get',url=self.server_b_host, 
                                        timeout=10)
        if r.ok:
            return True, self.server_b_host
        
        logger.error(r.error)

        return False, r.error

    async def send_data_server_b(self, data):
        print(data)
        return await safe_request(method='post', url=self.server_b_host+'/ip-geopoint/', 
                                  json=data, timeout=10, headers={"Content-Type": "application/json"})

    async def get_data_server_b(self, params: dict) -> Response:
        if not params:
            url = self.server_b_host+'/all-ip-geopoints/'
        else:
            url = self.server_b_host+'/ip-geopoint/'
        return await safe_request(method='get', url=url, params=params,
                                timeout=10)
        

class LogicService:
    
    def __init__(self, send_callback: Callable[[dict], Awaitable[Response]], 
                 get_callback: Callable[[Optional[dict]], Awaitable[Response]]):
        
        self._send_server_b = send_callback
        self._get_server_b = get_callback


    async def lookup_ip(self, ip: IPvAnyAddress) -> Response:
        return await safe_request(method='get', url=IP_LOC_URL.format(ip))
    
    def create_location(self, ip: IPvAnyAddress, data: dict) -> IpLocation:
        return IpLocation(ip=str(ip), geo_point={"lat": data['lat'], "lon": data['lon']})
    
    async def send_location(self, location: IpLocation) -> tuple[bool, str]:
        r: Response = await self._send_server_b(location.model_dump())
        if not r.ok:
            return False, r.error
        return True, "Data sent successfully"

    async def process(self, ip: IPvAnyAddress) -> tuple[bool, str]:

        r: Response = await self.lookup_ip(ip)

        if not r.ok:
            return False, r.error
        
        ip_loc = self.create_location(ip, r.data)
        
        return await self.send_location(ip_loc)


    async def get_data_server_b(self, ip: Optional[IPvAnyAddress]) -> tuple[bool, list[IpLocation]|IpLocation]:
        param = {}
        if ip is not None:
            param = {'ip': ip}

        r: Response = await self._get_server_b(param)

        data =  r.data

        if not r.ok:
            r = await self.lookup_ip(ip) if ip is not None else r
        
        data = self.create_location(ip, r.data) if ip is not None else r.data

        return r.ok, data
    