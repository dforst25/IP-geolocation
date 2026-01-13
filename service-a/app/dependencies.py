import os
from socket import timeout
from fastapi import Depends

from services import CommunicationService, LogicService


def get_communication_service() -> CommunicationService:
    server_b_host = os.getenv("SERVER_B_HOST", "http://localhost")
    server_b_port = os.getenv("SERVER_B_PORT", "")

    return CommunicationService(server_b_host, server_b_port, timeout)




def get_logic_service(
    comm_service: CommunicationService = Depends(get_communication_service)
) -> LogicService:

    return LogicService(send_callback=comm_service.send_data_server_b)
