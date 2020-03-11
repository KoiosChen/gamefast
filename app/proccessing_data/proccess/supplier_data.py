from ... import db, logger
from flask import jsonify, session
from ...models import LineDataBank, Domains, Customer, MachineRoom, Vlan, Contacts, User, Interfaces, Cloud, VXLAN, \
    IPSupplier, IPManager, IPGroup, DNSManager, DIA
from ...proccessing_data.get_datatable import make_table, make_table_ip_supplier, make_table_supplier_ip, make_table_ip
from ...validate.verify_fields import verify_fields, chain_add_validate, verify_required, verify_network, \
    verify_net_in_net
import datetime
from .public_methods import contacts_update, vlan_update, new_data_obj


def supplier_update(contents, line_obj):
    interconnection_dict = dict()
    vlan_dict = dict()
    contact_dict = dict()
    for k, v in contents.items():
        if k == 'a_pop_interface_id' and v:
            setattr(line_obj, 'line_access_interface', v)
        if k == 'mode' and v:
            setattr(line_obj, k, v)

        if k in ['start_time', 'stop_time'] and v:
            vr = verify_fields('date', k, v)
            if vr is not True:
                return vr
            setattr(line_obj, k, datetime.datetime.strptime(v, '%Y-%m-%d'))

        if k in ['interconnection_supplier', 'interconnection_us', 'interconnection_netmask'] and v:
            interconnection_dict[k] = v

        if k in ['vlan', 'vlan_desc', 'vlan_type', 'vlan_map_to', 'qinq_inside'] and v:
            vlan_dict[k] = v

        if ('contact' in k or 'customer_manager' in k) and v:
            contact_dict[k] = v

    if vlan_dict:
        op_result = vlan_update(line_obj.access_vlan, vlan_dict)
        if op_result['status']:
            line_obj.access_vlan = op_result['data']
        else:
            return op_result['data']

    if interconnection_dict:
        map_dict = {'interconnection_us': 'IP',
                    'interconnection_supplier': 'gateway',
                    'interconnection_netmask': 'netmask'}
        unchanged_field = {'interconnection_supplier', 'interconnection_us', 'interconnection_netmask'} - set(
            interconnection_dict.keys())
        r = verify_required(**{k: v for k, v in interconnection_dict.items()})
        if r is not True:
            if not line_obj.interconnect_ip:
                return r
        else:
            if unchanged_field:
                for uf in list(unchanged_field):
                    interconnection_dict[uf] = getattr(line_obj.ip_a_z, map_dict.get(uf))

            r = verify_network(**{map_dict[k]: v for k, v in interconnection_dict.items()})
            if r is not True:
                return r
            if not line_obj.interconnect_ip:
                new_ip = new_data_obj('IPManager',
                                      **{"IP": interconnection_dict.get('interconnection_us'),
                                         "netmask": interconnection_dict.get('interconnection_netmask'),
                                         "gateway": interconnection_dict.get('interconnection_supplier')})
                db.session.add(new_ip)
                line_obj.ip_a_z = new_ip
            else:
                for kk, vv in interconnection_dict.items():
                    setattr(line_obj.ip_a_z, map_dict.get(kk), vv)

    if contact_dict:
        contact_update_result = contacts_update(line_obj, contact_dict, 'supplier')
        if contact_update_result is not True:
            return contact_update_result

    # 更新操作人、操作时间
    if not line_obj.line_operator:
        line_obj.line_operator = session['SELFID']
        line_obj.operate_time = datetime.datetime.now()
    db.session.add(line_obj)
    db.session.commit()
    return make_table_ip_supplier([line_obj])


def supplier_ip_update(contents, line_obj):
    print(contents)
    import ipaddress
    if not contents.get('site'):
        return {'error': '未选择供应商'}
    supplier_id = contents.get('site').split('_')[1]

    contents['IP'] = contents.get('ip')
    supplier = IPSupplier.query.get(int(supplier_id))
    line_attr = {'IP', 'netmask', 'gateway', 'dns', 'isp', 'desc', 'available_ip'}
    updated_attr = set(contents.keys()) & line_attr
    ip_group = supplier.available_ip_group

    if contents.get('dns'):
        try:
            ipaddress.ip_address(contents.get('dns'))
            dns_ = new_data_obj('DNSManager', **{'dns': contents.get('dns')})
        except ValueError:
            logger.error(f'DNS IP format error {contents.get("dns")}')
            return {'fieldErrors': [{'name': 'dns', 'status': 'DNS 格式错误'}]}

    if not line_obj:
        if supplier.mode == 2:
            vr = verify_required(**{'ip': contents.get('ip'), 'netmask': contents.get('netmask')})
            if vr is not True:
                return vr
            else:
                try:
                    ip_network = ipaddress.ip_network(contents['ip'] + '/' + contents['netmask'], strict=False)
                    contents['ip'] = str(ip_network[0])
                    contents['gateway'] = ''
                except ValueError:
                    return {'error': "格式错误"}
        else:
            vr = verify_required(**{'ip': contents.get('ip'),
                                    'netmask': contents.get('netmask'),
                                    'gateway': contents.get('gateway')})
            if vr is not True:
                return vr

            try:
                vn = verify_network(**{'IP': contents.get('ip'), 'netmask': contents.get('netmask'),
                                       'gateway': contents.get('gateway')})
                if vn is not True:
                    return vn
            except Exception as e:
                logger.error(e)
                return {'error': 'IP地址段不符合'}

            try:
                ip_network = ipaddress.ip_network(contents['ip'] + '/' + contents['netmask'], strict=False)
            except ValueError:
                return {'error': "格式错误"}

        if not ip_group:
            ip_group = IPGroup(group_name=f'For supplier {supplier.line_code}')
            db.session.add(ip_group)

        new_ip = new_data_obj('IPManager',
                              **{'IP': contents['ip'],
                                 'netmask': contents['netmask'],
                                 'desc': f"For supplier {supplier.line_code}",
                                 'gateway': contents.get('gateway'),
                                 'available_ip': contents.get('available_ip') if contents.get('available_ip') else str(
                                     ip_network[1]) + '-' + str(ip_network[-2]),
                                 'isp': contents.get('isp', '')})
        if contents.get('dns'):
            new_ip.ip_dns = dns_

        new_ip.group = ip_group

        supplier.available_ip_group = ip_group
        db.session.add(supplier)
        db.session.commit()
    return {'data': make_table_supplier_ip(supplier.available_ip_group.ip_list.all())}
