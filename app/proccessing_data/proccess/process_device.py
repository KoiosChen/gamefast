from ...models import MachineRoom, Device, Customer, Platforms
from flask import jsonify
from ... import db, logger
from ..proccess.public_methods import new_data_obj
from ...common import db_commit, success_return, false_return


def new_one(**kwargs):
    """
    {'device_name': row[0].value,
         'device_ip': row[1].value,
         'device_owner': row[2].value,
         'username': row[3].value,
         'password': row[4].value,
         'enable_password': row[5].value,
         'login_method': row[6].value,
         'monitor_status': row[7].value,
         'device_vendor': row[8].value,
         'device_model': row[9].value,
         'machine_room': row[10].value
         }
    new_device["device_name"] = content.get("device_name")
    new_device["device_ip"] = content.get("device_ip")
    new_device["vendor"] = content.get("vendor")
    new_device["device_model"] = content.get("device_model")
    new_device["machine_room"] = content.get("machine_room_id")
    new_device["os_version"] = content.get("os_version")
    new_device["patch_version"] = content.get("patch_version")
    new_device["serial_number"] = content.get("serial_number")
    new_device["login_method"] = content.get("login_method")
    new_device["login_name"] = content.get("login_name")
    new_device["login_password"] = content.get("login_password")
    new_device["enable_password"] = content.get("enable_password")
    new_device["device_owner"] = content.get("device_belong_id")
    :param kwargs:
    :return:
    """
    device_name = kwargs.get("device_name")
    device_model = kwargs.get("device_model")
    device_ip = kwargs.get("device_ip")
    device_owner = kwargs.get("device_owner")
    login_method = kwargs.get("login_method", "")
    username = kwargs.get("username")
    password = kwargs.get("password")
    enable_password = kwargs.get("enable_password")
    machine_room = kwargs.get("machine_room")
    os_version = kwargs.get("os_version", "")
    patch_version = kwargs.get("patch_version", "")
    serial_number = kwargs.get("serial_number", "")
    vendor = kwargs.get("device_vendor", "")
    community = kwargs.get("community", "")
    platform = kwargs.setdefault("platform", "")

    logger.debug(kwargs)

    if Device.query.filter(Device.ip.__eq__(device_ip), Device.device_name.__eq__(device_name)).first():
        return {"status": False, "content": f"{device_name} - {device_ip} {device_model} exist"}

    else:
        try:
            machine_room_id = eval(machine_room)
            mr = MachineRoom.query.filter_by(id=machine_room_id, status=1).first()
        except NameError:
            mr = MachineRoom.query.filter_by(name=machine_room, status=1).first()

        try:
            device_owner_id = eval(device_owner)
            owner = Customer.query.get(device_owner_id)
        except NameError:
            owner = new_data_obj("Customer", **{"name": device_owner})

        new_device = Device(device_name=device_name,
                            device_owner=owner,
                            ip=device_ip,
                            login_method=login_method,
                            login_name=username,
                            login_password=password,
                            enable_password=enable_password,
                            machine_room=mr,
                            device_model=device_model,
                            vendor=vendor,
                            os_version=os_version,
                            patch_version=patch_version,
                            serial_number=serial_number,
                            community=community
                            )
        if platform:
            try:
                platform_id = eval(platform)
                device_platform = Platforms.query.get(platform_id)
            except NameError:
                device_platform = new_data_obj("Platforms", **{"name": platform})
            new_device.device_platform = device_platform
        db.session.add(new_device)
        return success_return(new_device, "") if db_commit() else false_return('', 'add device fail')
