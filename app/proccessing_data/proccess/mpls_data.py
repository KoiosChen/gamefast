from ... import db, logger
from ...models import LineDataBank, IPSupplier, IPManager, IPGroup, DIA
from ...proccessing_data.get_datatable import make_table_mpls_attribute, make_table_ip
from ...validate.verify_fields import verify_fields, verify_required, verify_network, verify_net_in_net
import re
from .public_methods import new_data_obj, new_linecode


def mpls_route_new(content):
    from IPy import IP
    logger.debug(content)
    if not content.get('site'):
        return {'error': '未选择线路'}
    line_id = content.get('site').split('_')[1]
    line = LineDataBank.query.get(line_id)
    mpls = line.mpls_attribute.first()
    if mpls is None:
        mpls = new_data_obj("MPLS", **{"line_id": line_id})
    _ip = content.get('route_ip')
    _netmask = content.get('route_netmask')

    vr = verify_required(**{'ip': _ip, 'netmask': _netmask})
    if vr is not True:
        return vr

    vf = verify_fields('netmask', 'route_netmask', _netmask)
    if vf is not True:
        return vf

    vf = verify_fields('IP', 'route_ip', _ip)
    if vf is not True:
        return vf

    if not mpls.mpls_route_ip:
        new_mpls_route_group = IPGroup(group_name=f'For {line.line_code}, vrf {mpls.vrf}')
        db.session.add(new_mpls_route_group)
        mpls.mpls_route_ip = new_mpls_route_group

    if int(_netmask) < 32:
        _ip = IP(_ip + '/' + _netmask, make_net=True).strNormal(0)

    new_route = new_data_obj("IPManager", **{"IP": _ip, "netmask": _netmask})

    mpls.mpls_route_ip.ip_list.append(new_route)
    db.session.commit()
    return {'data': make_table_mpls_attribute([new_route])}


def mpls_route_update(contents, line_obj):
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
