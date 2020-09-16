from ... import db, logger
from ...models import Device
from ...proccessing_data.get_datatable import make_table_device
from ...validate.verify_fields import verify_fields, verify_required, verify_network, verify_net_in_net
import re
from .public_methods import new_data_obj, new_linecode
from . import process_device
from ...common import db_commit
from flask import jsonify
from ...MyModule.SyncDevice import do_sync


def device_new(contents):
    """

    :param contents:
    :return:
    """
    vr = verify_required(
        **{"device_name": contents.get("device_name"),
           "device_ip": contents.get("device_ip"),
           "machine_room_id": contents.get("machine_room_id"),
           "platform_id": contents.get("platform_id"),
           "vendor": contents.get("vendor"),
           "device_belong_id": contents.get("device_belong_id")})
    if vr is not True:
        return vr

    vr = verify_fields("IP", "device_ip", contents.get("device_ip"))
    if vr is not True:
        return vr

    if Device.query.filter_by(device_name=contents.get("device_name")).first():
        return {"fieldErrors": [{"name": "device_name", "status": "设备名已存在"}]}

    if Device.query.filter_by(ip=contents.get("device_ip")).first():
        return {"fieldErrors": [{"name": "device_ip", "status": "设备管理地址已存在"}]}

    new_device = {"device_name": contents.get("device_name"),
                  "device_ip": contents.get("device_ip"),
                  "device_vendor": contents.get("vendor"),
                  "device_model": contents.get("device_model"),
                  "machine_room": contents.get("machine_room_id"),
                  "os_version": contents.get("os_version"),
                  "patch_version": contents.get("patch_version"),
                  "serial_number": contents.get("serial_number"),
                  "login_method": contents.get("login_method"),
                  "username": contents.get("login_name"),
                  "password": contents.get("login_password"),
                  "enable_password": contents.get("enable_password"),
                  "device_owner": contents.get("device_belong_id"),
                  "community": contents.get("community"),
                  "platform": contents.get("platform_id")}
    process_result = process_device.new_one(**new_device)
    if process_result.get("code") == "success":
        if contents.get("sync_device_info") == "YES":
            logger.info(f"start to sync device {contents.get('device_ip')}")
            do_sync([process_result.get("data")], "interface")
        return {'data': make_table_device([process_result.get("data")])}


def device_update(contents, line_obj):
    logger.debug(f'In device update {contents}')
    changed_fields = list(contents.keys())
    # 可直接更新的字段
    update_direct = {'device_name', 'device_ip', 'machine_room_id', 'vendor', 'device_model', 'os_version',
                     'patch_version', 'serial_number', 'community', 'login_method', 'login_name', 'login_password',
                     'enable_password', 'device_belong_id', 'platform_id'} & set(changed_fields)
    if update_direct:
        for f in list(update_direct):
            field = "_".join(f.split("_")[0:2]) if f == 'device_belong_id' else f
            if f == 'device_ip':
                vr = verify_fields("IP", "device_ip", contents.get(f))
                if vr is not True:
                    return vr
                else:
                    if Device.query.filter_by(ip=contents.get("device_ip")).first():
                        return {"fieldErrors": [{"name": "device_ip", "status": "设备管理地址已存在"}]}
                    field = "ip"
            setattr(line_obj, field, contents.get(f))
        db.session.add(line_obj)

    return {'data': make_table_device([line_obj])} if db_commit() else {"error": "更新失败，设备名称冲突"}
