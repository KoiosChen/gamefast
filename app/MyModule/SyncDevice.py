from .. import logger, redis_db, db
from ..models import Device, SYNC_DEVICE_URL
import requests
from ..MyModule.RequestPost import post_request
import uuid


def do_sync(devices, sync_content):
    """

    :param devices:
    :param sync_content:
    :return:
    """
    if not devices:
        devices = Device.query.filter_by(status=1).all()

    for device in devices:
        post_request(SYNC_DEVICE_URL.get(sync_content),
                     {'ip': device.ip,
                      'order_number': device.ip,
                      'username': device.login_name,
                      'password': device.login_password,
                      'vendor': device.vendor,
                      'device_model': device.device_model},
                     'sync_' + sync_content + '_' + device.ip)
