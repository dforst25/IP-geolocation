import logging
from typing import Callable, Optional, Awaitable


from utils import safe_request, Response
from models import IpLocation, Ip


IP_LOC_URL = "http://ip-api.com/json/{}"

logger = logging.getLogger(__name__)

class CommunicationService:
    
    def __init__(self, server_b_host, server_b_port='', timeout=10):


        self.__server_b_host = server_b_host

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
                                        timeout=self.__timeout)
        if r.ok:
            return True, self.server_b_host
        
        logger.error(r.error)

        return False, r.error

    async def send_data_server_b(self, data):
        return await safe_request(method='post', url=self.server_b_host+'/ip-geopoint', 
                                  json=data, timeout=self.__timeout)

    async def get_data_server_b(self, params: dict[str, Any]) -> Response:
        return await safe_request(method='get', url=self.server_b_host+'/ip-geopoint', params=params,
                                timeout=self.__timeout)
        

class LogicService:
    
    def __init__(self, send_callback: Callable[[dict], Awaitable[Response]], 
                 get_callback: Callable[[Optional[dict]], Awaitable[Response]]):
        
        self._send_server_b = send_callback
        self._get_server_b = get_callback


    async def lookup_ip(self, ip: str) -> tuple[bool, dict | str]:

        r: Response = await safe_request(method='get', url=IP_LOC_URL.format(ip))
        if not r.ok:
            return False, r.error
        return True, r.data
    
    def create_location(self, ip: str, data: dict) -> IpLocation:
        return IpLocation(ip=ip, lat=data['lat'], lon=data['lon'])
    
    async def send_location(self, location: IpLocation) -> tuple[bool, str]:
        r: Response = await self._send_server_b(location.model_dump())
        if not r.ok:
            return False, r.error
        return True, "Data sent successfully"

    async def get_data_server_b(self, ip: Optional[Ip]) -> Response:
        param = {}
        if ip is not None:
            param = {'ip': ip.ip}

        return await self._get_server_b(param)

    async def process(self, ip: str) -> tuple[bool, str]:
        ok, data_or_error = await self.lookup_ip(ip)
        if not ok:
            return False, data_or_error

        location = self.create_location(ip, data_or_error)
        return await self.send_location(location)
