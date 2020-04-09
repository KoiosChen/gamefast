from ...models import MachineRoom
from sqlalchemy import or_
from ... import db, logger
from ...common import db_commit, success_return, false_return
from ...proccessing_data.proccess import public_methods


def new_one(**kwargs):
    machine_room_name = kwargs.get("machine_room_name")
    machine_room_address = kwargs.get("machine_room_address")
    machine_room_level = kwargs.get("machine_room_level")
    machine_room_type = kwargs.get("machine_room_type")
    machine_room_lift = kwargs.get("machine_room_lift")
    machine_room_city = kwargs.get("machine_room_city")
    machine_room_admin = kwargs.get("machine_room_admin")
    noc_contact_name = kwargs.get("noc_contact_name")
    noc_contact_phone = kwargs.get("noc_contact_phone")
    noc_contact_email = kwargs.get('noc_contact_email')

    logger.debug(kwargs)

    if MachineRoom.query.filter(or_(MachineRoom.name.__eq__(machine_room_name),
                                    MachineRoom.address.__eq__(machine_room_address))).all():
        return false_return("", f"{machine_room_name} or f{machine_room_address} exist")

    else:
        last_machine_room = MachineRoom.query.order_by(MachineRoom.id.desc()).first()
        if last_machine_room:
            permit_value = hex(int(last_machine_room.permit_value, 16) << 1)
        else:
            permit_value = hex(1)

        new_machine_room = MachineRoom(name=machine_room_name,
                                       address=machine_room_address,
                                       level=machine_room_level,
                                       status='1',
                                       permit_value=permit_value,
                                       type=machine_room_type,
                                       lift=True if machine_room_lift == '1' else False,
                                       city=machine_room_city)
        db.session.add(new_machine_room)
        commit_result = db_commit()
        if commit_result['code'] == 'success':
            if noc_contact_name:
                new_contact = public_methods.new_data_obj("Contacts",
                                                          **{"name": noc_contact_name, "phoneNumber": noc_contact_phone,
                                                             "email": noc_contact_email})
                db.session.add(new_contact)
            elif machine_room_admin:
                new_machine_room.noc_contact = machine_room_admin
        return success_return(data=new_machine_room, msg='机房添加成功') \
            if db_commit().get("code") == 'success' else false_return(msg='add machine room fail')
