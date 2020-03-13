from ... import db, logger
from ...models import LineDataBank, IPSupplier, IPManager, IPGroup, DIA, machineroom_type, machineroom_level, \
    MachineRoom
from ...proccessing_data.get_datatable import make_table_mpls_attribute, make_table_ip, make_table_machine_room
from ...validate.verify_fields import verify_fields, verify_required, verify_network, verify_net_in_net
import re
from .public_methods import new_data_obj, new_linecode
from . import process_machine_room
from ...common import db_commit
from flask import jsonify


def machine_room_new(content):
    """

    :param content:
    :return:
    """
    vr = verify_required(
        **{"name": content.get("name"),
           "address": content.get("address"),
           "level_id": content.get("level_id"),
           "type_id": content.get("type_id"),
           "a_pop_city_id": content.get("a_pop_city_id")})
    if vr is not True:
        return vr

    if MachineRoom.query.filter_by(name=content.get("name")).first():
        return {"fieldErrors": [{"name": "name", "status": "机房名已存在"}]}

    noc_contact = [c for c in content.keys() if "noc" in c and content.get(c)]

    if noc_contact:
        vr_name = verify_required(**{"noc_contact_name": content.get("noc_contact_name")})
        if vr_name is not True:
            return vr_name

        for c in noc_contact:
            vr = verify_fields(c.split('_')[2], c, content.get(c))
            if vr is not True:
                return vr

    new_machine_room = dict()
    new_machine_room["machine_room_name"] = content.get("name")
    new_machine_room["machine_room_address"] = content.get("address")
    new_machine_room["machine_room_level"] = content.get("level_id")
    new_machine_room["machine_room_type"] = content.get("type_id")
    new_machine_room["machine_room_lift"] = content.get("lift_id")
    new_machine_room["machine_room_city"] = content.get("a_pop_city_id")
    new_machine_room["machine_room_admin"] = content.get("noc_contact_name")
    process_result = process_machine_room.new_one(**new_machine_room)
    if process_result.get("code") == "success":
        return {'data': make_table_machine_room([process_result.get("data")])}


def machine_room_update(contents, line_obj):
    logger.debug(f'In machine room update {contents}')
    changed_fields = list(contents.keys())
    # 可直接更新的字段
    update_direct = {'address', 'a_pop_city_id', 'level_id', 'status_id', 'lift_id', 'type_id'} & set(changed_fields)
    lift_dict = {'1': True, '0': False}
    if update_direct:
        for f in list(update_direct):
            field = f.split("_")[-2] if "id" in f else f
            setattr(line_obj, field, lift_dict[contents.get(f)] if 'lift' in f else contents.get(f))
        db.session.add(line_obj)

        # if {'a_pop_city_id', 'level_id', 'type_id'} & set(changed_fields):
        #     setattr(line_obj, 'name',
        #             line_obj.cities.city + machineroom_level[str(line_obj.level)] + machineroom_type[str(line_obj.type)])
        #     db.session.add(line_obj)

    return {'data': make_table_machine_room([line_obj])} if db_commit() else {"error": "更新失败，机房名称冲突"}
