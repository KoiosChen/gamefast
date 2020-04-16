import requests
import threading
from .. import logger, redis_db
from ..MyModule.RequestPost import post_request
from ..models import API_URL
import uuid
import json


def verify_ring(line):
    logger.debug('verfiy rrpp ' + str(line.id))
    api_url = API_URL.get("verify_ring")
    if line.a_interface and line.z_interface and line.line_platform and line.vlans and line.main_route and line.domains:
        send_content = {"order_number": line.line_code,
                        "a_city": line.a_interface.device_interface.machine_room.cities.city,
                        "z_city": line.z_interface.device_interface.machine_room.cities.city,
                        "platform": line.line_platform.name,
                        "vlan": line.vlans.name,
                        "domains": '_'.join(sorted([d.name for d in line.domains]))}
        post_request(url=api_url, value=send_content, request_lock=f'check_rrpp_lock::{line.line_code}')
        return True
    else:
        return False
