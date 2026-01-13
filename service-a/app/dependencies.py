import os
from socket import timeout
from fastapi import Depends

from services import CommunicationService, LogicService


def get_communication_service() -> CommunicationService:
    server_b_host = os.getenv("SERVER_B_HOST", "192.168.30.64")
    server_b_port = os.getenv("SERVER_B_PORT", "8001")

    return CommunicationService(server_b_host, server_b_port, timeout)

def get_logic_service(
    comm_service: CommunicationService = Depends(get_communication_service)
) -> LogicService:

    return LogicService(send_callback=comm_service.send_data_server_b,
                        get_callback=comm_service.get_data_server_b)
