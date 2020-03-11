from ... import db, logger
from ...models import LineDataBank, IPSupplier, IPManager, IPGroup, DIA
from ...proccessing_data.get_datatable import make_table_mpls_attribute, make_table_ip
from ...validate.verify_fields import verify_fields, verify_required, verify_network, verify_net_in_net
import re
from .public_methods import new_data_obj, new_linecode
from . import process_machine_room


def machine_room_new(content):
    """

    :param content:
    :return:
    """
    vr = verify_required(
        **{"name": content.get("name"),
           "address": content.get("address"),
           "level": content.get("level"),
           "type": content.get("type"),
           "a_pop_city_id": content.get("a_pop_city_id")})
    if vr is not True:
        return vr

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
    new_machine_room["machine_room_level"] = content.get("level")
    new_machine_room["machine_room_type"] = content.get("type")
    new_machine_room["machine_room_lift"] = content.get("lift")
    new_machine_room["machine_room_city"] = content.get("a_pop_city_id")
    new_machine_room["machine_room_admin"] = content.get("noc_contact_name")
    process_machine_room.new_one(**new_machine_room)


def machine_room_update(contents, line_obj):
    logger.debug(f'in mpls route update {contents}')
    from IPy import IP
    required_fields = {'route_ip', 'route_netmask'}
    required_fields_map = {"route_ip": "IP", "route_netmask": "netmask"}
    changed_field = required_fields & set(contents.keys())
    if changed_field:
        ip = contents.get('route_ip', line_obj.IP)
        netmask = contents.get('route)netmask', line_obj.netmask)
        try:
            vn = verify_fields('netmask', 'route_netmask', netmask)
            if vn is not True:
                return vn
            IP(ip)
        except ValueError:
            return {'fieldErrors': [{'name': 'route_ip', 'status': 'IP地址格式错误'}]}

        if int(netmask) < 32:
            contents['route_ip'] = IP(ip + '/' + netmask, make_net=True).strNormal(0)

        for k, v in contents.items():
            if hasattr(line_obj, required_fields_map.get(k, "")):
                setattr(line_obj, required_fields_map[k], v)

        return {'data': make_table_mpls_attribute([line_obj])}
