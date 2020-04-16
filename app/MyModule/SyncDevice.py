from .. import logger, redis_db, db
from ..models import Device, API_URL
import requests
from ..MyModule.RequestPost import post_request
import uuid
from ..common import success_return, false_return


def do_sync(devices, sync_content):
    """

    :param devices:
    :param sync_content:
    :return:
    """
    if not devices:
        devices = Device.query.filter_by(status=1).all()

    results = list()
    for device in devices:
        if device:
            result = post_request(API_URL.get(sync_content),
                                  {
                                      'ip': device.ip,
                                      'order_number': device.ip,
                                      'username': device.login_name,
                                      'password': device.login_password,
                                      'vendor': device.vendor,
                                      'device_model': device.device_model
                                  },
                                  'sync_' + sync_content + '::' + device.ip)
            logger.info(f"request result {result}")
            results.append(result.get("msg"))
    return success_return(msg=results)
