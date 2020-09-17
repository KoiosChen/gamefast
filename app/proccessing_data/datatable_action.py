from .. import db, logger
from flask import jsonify, session
from ..models import LineDataBank, Domains, Customer, MachineRoom, Vlan, Contacts, User, Interfaces, Cloud, VXLAN, \
    IPSupplier, IPManager, IPGroup, DNSManager, DIA, MPLS, Device
from ..proccessing_data.get_datatable import make_table, make_table_ip_supplier, make_table_supplier_ip, make_table_ip, \
    make_table_mpls, make_table_vxlan, make_table_dia
from ..validate.verify_fields import verify_fields, chain_add_validate, verify_required, verify_network, \
    verify_net_in_net
from ..validate.verify_ring import verify_ring
from ..common import db_commit
import re
import datetime
from .proccess.mpls_data import mpls_route_update, mpls_route_new
from .proccess.dia_data import dia_ip_new, dia_ip_update
from .proccess.public_methods import new_linecode, new_data_obj
from .proccess.supplier_data import supplier_ip_update, supplier_update
from .proccess.machine_room_data import machine_room_update, machine_room_new
from .proccess.device_data import device_new, device_update


def do_edit(dt, func, data):
    logger.info(f'Do edit for {dt} using function {func}')
    logger.debug(f'The data is {data}')
    return_data = list()
    for row_id, contents in data.items():
        line = eval(dt).query.get(row_id.split('_')[1])
        logger.debug(f'The db line is {line}')
        update_result = eval(func)(contents, line)
        if isinstance(update_result, dict):
            return jsonify(update_result)
        elif isinstance(update_result, list):
            return_data.extend(update_result)

    return jsonify({
        "data": return_data
    })


def edit(data):
    return do_edit('LineDataBank', 'line_update', data)


def edit_supplier(data):
    return do_edit('IPSupplier', 'supplier_update', data)


def edit_supplier_ip(data):
    return do_edit('IPManager', 'supplier_ip_update', data)


def edit_dia_ip(data):
    return do_edit('IPManager', 'dia_ip_update', data)


def edit_mpls_route(data):
    return do_edit('IPManager', 'mpls_route_update', data)


def edit_mpls(data):
    return do_edit('LineDataBank', 'mpls_update', data)


def edit_machine_room(data):
    return do_edit("MachineRoom", "machine_room_update", data)


def edit_device(data):
    return do_edit("Device", "device_update", data)


def remove_device(data):
    logger.debug(data)
    row_id = list(data.keys())[0].split("_")[1]
    delete_device = Device.query.get(int(row_id))
    delete_device.status = 0
    db.session.add(delete_device)
    return jsonify({"data": []}) if db_commit() else jsonify({'error': "删除失败"})


def remove_machine_room(data):
    logger.debug(data)
    row_id = list(data.keys())[0].split("_")[1]
    delete_machine_room = MachineRoom.query.get(int(row_id))
    db.session.delete(delete_machine_room)
    return jsonify({"data": []}) if db_commit() else jsonify({'error': "删除失败"})


def create_dia_ip(data):
    return jsonify(dia_ip_new(data['0'], None))


def create_supplier_ip(data):
    return jsonify(supplier_ip_update(data['0'], None))


def create_machine_room(data):
    return jsonify(machine_room_new(data['0']))


def create_device(data):
    return jsonify(device_new(data['0']))


def create_supplier(info):
    logger.debug(info)
    map_dict = {'interconnection_us': 'IP',
                'interconnection_supplier': 'gateway',
                'interconnection_netmask': 'netmask'}
    i = info['0']
    vr = {'supplier_name': i.get('supplier_name'),
          'bandwidth': i.get('bandwidth')}
    r = verify_required(**vr)
    if r is not True:
        return r
    __supplier = new_data_obj('Customer', **{'name': i.get('supplier_name'), 'status': 1})
    new_supplier = IPSupplier(supplier=__supplier, line_code='ISP-' + new_linecode(), bandwidth=i.get('bandwidth'),
                              bandwidth_unit=i.get('bandwidth_unit'))

    interconnection_list = list()
    vlan_list = list()
    contact_list = list()

    for k, v in i.items():
        if k == 'a_pop_interface_id' and v:
            setattr(new_supplier, 'line_access_interface', v)
        if k == 'mode' and v:
            setattr(new_supplier, k, v)

        if k in ['start_time', 'stop_time'] and v:
            vr = verify_fields('date', k, v)
            if vr is not True:
                return vr
            setattr(new_supplier, k, datetime.datetime.strptime(v, '%Y-%m-%d'))

        if k in ['interconnection_supplier', 'interconnection_us', 'interconnection_netmask'] and v:
            interconnection_list.append(k)

        if k in ['vlan', 'vlan_desc', 'vlan_type', 'vlan_map_to', 'qinq_inside'] and v:
            vlan_list.append(k)

        if ('contact' in k or 'customer_manager' in k) and v:
            contact_list.append(k)

    if interconnection_list:
        r = verify_required(**{k: i.get(k) for k in interconnection_list})
        if r is not True:
            return r
        else:
            r = verify_network(**{map_dict[k]: i.get(k) for k in interconnection_list})
            if r is not True:
                return r
            new_ip = new_data_obj('IPManager',
                                  **{"IP": i.get('interconnection_us'), "netmask": i.get('interconnection_netmask'),
                                     "gateway": i.get('interconnection_supplier')})
            db.session.add(new_ip)
            new_supplier.ip_a_z = new_ip

    db.session.add(__supplier)
    db.session.add(new_supplier)
    db.session.commit()

    return jsonify({"data": make_table_ip_supplier([new_supplier])})


def create_mpls_route(data):
    return mpls_route_new(data['0'])


def oss_operator(**kwargs):
    logger.debug(kwargs)

    __customer = new_data_obj('Customer', **{'name': kwargs.get('customer').strip(), 'status': 1})

    new = new_data_obj('LineDataBank',
                       **{'line_code': kwargs.get('line_code'), 'record_status': 1, 'customer': __customer.id})

    for key, value in kwargs.items():
        logger.debug(f'{key} {value}')
        if key in {'line_status', 'a_client_addr', 'z_client_addr', 'product_type', 'product_model', 'operate_time'}:
            if hasattr(new, key):
                try:
                    if key == 'line_status' and not isinstance(eval(value), int):
                        continue
                    elif value == 'None':
                        continue
                    else:
                        setattr(new, key, value)
                except Exception as e:
                    logger.error(f">>> The attribute {key} value {value} set fail for {e}")

        elif key == 'channel':
            logger.debug(f'channel value is {value}')
            for k, v in value.items():
                if hasattr(new, key + '_' + k):
                    try:
                        if k == 'number' and re.search(r'\d+\.?\d*', v):
                            _number = re.findall(r'(\d+\.?\d*)', v)[0]
                        setattr(new, key + '_' + k, eval(v) if 'number' == k else v)
                    except Exception as e:
                        logger.error(f">>> The attribute {key} value {value} set fail for {e}")
                        db.session.rollback()
                        line_desc = new.line_desc if new.line_desc else ""
                        setattr(new, 'line_desc', str(line_desc) + str(v))

        elif key == 'operator':
            if not User.query.filter_by(username=value, status=1).first():
                logger.error(f'operator {value} not in User table')
            else:
                new_user = User.query.filter_by(username=value, status=1).first()
                setattr(new, 'operator', new_user)

        elif key in {'biz_contact', 'noc_contact', 'customer_manager'}:
            if not Contacts.query.filter_by(name=value['name'],
                                            customers=__customer if 'customer' not in key else Customer.query.get(1),
                                            type=key).first():
                new_contact = Contacts(name=value['name'],
                                       phoneNumber=value['phoneNumber'],
                                       email=value['email'],
                                       address=value['address'],
                                       customers=__customer if 'customer' not in key else Customer.query.get(1),
                                       type=key)
                db.session.add(new_contact)
            else:
                new_contact = Contacts.query.filter_by(name=value['name'],
                                                       customers=__customer if 'customer' not in key else Customer.query.get(
                                                           1),
                                                       type=key).first()

            setattr(new, key + '_contact' if key == 'customer_manager' else key, new_contact)

    if kwargs.get('original') == 'oss':
        try:
            db.session.commit()
            logger.info('新(更新)线路资料{}插入成功'.format(kwargs.get('line_code')))
            return {'status': 'true', 'content': f"新（更新）线路资料{kwargs.get('line_code')}成功"}
        except Exception as e:
            logger.error(f'{e}')
            db.session.rollback()
            return {'status': 'false', 'content': f"新（更新）线路资料{kwargs.get('line_code')}失败"}


def line_update(line_data, line_obj):
    """
    used to update the line data bank fields
    :param line_data:
    :param line_obj:
    :return:
    """
    verify_ring_flag = False

    # operate vlan function

    def __op_vlan(line, vlan_class, vlan_type):
        """
        used to operate vlans
        :param line: sqlalchemy object of line_data_bank
        :param vlan_class:
        :param vlan_type:
        :return:
        """
        if vlan_class == 'vlan':
            if vlan_class in to_update.keys():
                if re.search(r'\D+', to_update.get(vlan_class)) and vlan_type in ('access', 'vxlan'):
                    return {
                        "fieldErrors": [
                            {
                                "name": "vlan",
                                "status": "非法字符"
                            }
                        ]
                    }
                v = verify_fields('vlan', vlan_class, to_update.get(vlan_class), vlan_type)
                if isinstance(v, dict):
                    return v
                if line.vlans and line.vlans.name == to_update.get(vlan_class):
                    for c in line.vlans.children:
                        db.session.delete(c)
                    line.vlans.type = vlan_type

                elif (line.vlans and line.vlans.name != to_update.get(vlan_class)) or not line.vlans:
                    new_vlan = Vlan(name=to_update.get(vlan_class), type=vlan_type)

                    old_children = list()
                    if line.vlans and line.vlans.children:
                        old_children = line.vlans.children

                    db.session.add(new_vlan)

                    line.vlans = new_vlan

                    if old_children:
                        for oc in old_children:
                            line.vlans.children.append(oc)

            elif vlan_class not in to_update.keys() and line.vlans:
                if re.search(r'\D+', line.vlans.name) and vlan_type in ('access', 'vxlan'):
                    return {
                        "fieldErrors": [
                            {
                                "name": "vlan",
                                "status": "非法字符"
                            }
                        ]
                    }
                line.vlans.type = vlan_type
                for c in line.vlans.children:
                    db.session.delete(c)
            else:
                return {'error': "Vlan错误，请重新选择"}
            return True
        elif vlan_class in ('qinq_inside', 'vxlan_inside', 'vlan_map_to'):
            if vlan_class in to_update.keys():
                if vlan_class == 'vlan_map_to':
                    if re.search(r'\D+', to_update.get(vlan_class)):
                        return {
                            "fieldErrors": [
                                {
                                    "name": "vlan_map_to",
                                    "status": "仅数值（1-4096）"
                                }
                            ]
                        }
                value = to_update.get(vlan_class).replace('，', ',')
                v = verify_fields('vlan', vlan_class, value)
                if isinstance(v, dict):
                    return v

                if line.vlans and line.vlans.children and value in line.vlans.children:
                    pass
                elif line.vlans and (
                        (line.vlans.children and value not in line.vlans.children) or not line.vlans.children):
                    for c in line.vlans.children:
                        db.session.delete(c)
                    new_vlan = Vlan(name=value, type=vlan_class)
                    db.session.add(new_vlan)
                    line.vlans.children.append(new_vlan)
                elif not line.vlans:
                    return {'error': '缺少 {} Vlan'.format(vlan_type)}
            elif vlan_class not in to_update.keys() and line.vlans and line.vlans.children:
                for c in line.vlans.children:
                    c.type = vlan_class
            elif vlan_class not in to_update.keys() and (not line.vlans or (line.vlans and not line.vlans.children)):
                return {'error': '缺少必要Vlan'}
            return True

    l = line_obj
    contents = line_data
    to_update = {}
    for field, value in contents.items():
        if field in ['line_code', 'customer_name', 'channel_type', 'channel_number', 'channel_unit',
                     'line_operator', 'operate_time']:
            logger.debug("不可修改字段")
            return {"error": "不可修改此字段"}

        elif (field in ['a_chain', 'main_route', 'z_chain'] and value) or (
                field not in ['a_chain', 'main_route', 'z_chain', 'search_city', 'search_city_z', 'search_city_a']):
            # 格式化去掉两头空格
            value = value.strip() if isinstance(value, str) else value
            to_update[field] = value

    logger.debug(to_update)

    contacts = {'biz_contact_name', 'noc_contact_name', 'customer_manager_name', 'biz_contact_phoneNumber',
                'biz_contact_email', 'noc_contact_phoneNumber', 'noc_contact_email', 'customer_manager_phoneNumber'}

    contacts_to_update = contacts & set(to_update.keys())

    # contacts update
    if contacts_to_update:
        # if not validate(to_update.get(''))
        for contact in contacts_to_update:
            for k in ('name', 'email', ' phone'):
                if k in contact and to_update.get(contact):
                    k_v = verify_fields(k, contact, to_update.get(contact))
                    if isinstance(k_v, dict):
                        return k_v

        # 若有修改名字，那么就直接重新创建一个联系人
        name_set = {'biz_contact_name', 'noc_contact_name', 'customer_manager_name'} & set(to_update.keys())
        if name_set:
            the_contact_name = list(name_set)[0]
            contact_attr_prefix = '_'.join(the_contact_name.split('_')[:2])
            contact_attr_name = contact_attr_prefix if 'customer' not in the_contact_name else contact_attr_prefix + '_contact'
            contact_field = the_contact_name.split('_')[-1]
            new_contact = Contacts()
            setattr(new_contact, contact_field, to_update.get(the_contact_name))
            other_attr = {'biz_contact_phoneNumber', 'biz_contact_email', 'noc_contact_phoneNumber', 'noc_contact_email', 'customer_manager_phoneNumber'} & set(to_update.keys())
            if other_attr:
                for other_k in other_attr:
                    contact_field = other_k.split('_')[-1]
                    setattr(new_contact, contact_field, to_update.get(other_k))
            setattr(l, contact_attr_name, new_contact)
            db.session.add(new_contact)
            db.session.add(l)
        else:
            for contact in contacts_to_update:
                contact_attr = '_'.join(contact.split('_')[:2]) if 'customer' not in contact else '_'.join(
                    contact.split('_')[:2]) + '_contact'
                contact_field = contact.split('_')[-1]
                if hasattr(l, contact_attr) and getattr(l, contact_attr):
                    now_contact = getattr(l, contact_attr)
                    setattr(now_contact, contact_field, to_update.get(contact))
                elif hasattr(l, contact_attr) and not getattr(l, contact_attr):
                    pass

    if 'bd' in to_update.keys():
        the_vxlan = l.vxlan_attribute.all()
        if the_vxlan:
            the_vxlan[0].bd = to_update['bd']
        else:
            new_vxlan = VXLAN(bd=to_update['bd'], desc=l.line_code, line_id=l.id)
            db.session.add(new_vxlan)

    if 'mode' in to_update.keys():
        the_dia = l.dia_attribute.all()
        if the_dia:
            the_dia[0].mode = to_update['mode']
        else:
            new_dia = DIA(line_id=l.id)
            db.session.add(new_dia)

    mpls_attribute_update_key = {'access_way', 'route_protocol', 'as_number', 'vrf', 'rt', 'interconnect_client',
                                 'interconnect_netmask', 'interconnect_pe'} & set(to_update.keys())

    if mpls_attribute_update_key:
        all_sub_lines = LineDataBank.query.filter_by(line_code=l.line_code).all()
        the_mpls = l.mpls_attribute.first()
        if not the_mpls:
            the_mpls = MPLS(line_id=l.id)
            db.session.add(the_mpls)
        interconnect = list()
        for k in mpls_attribute_update_key:
            if k in ('vrf', 'rt'):
                for sub in all_sub_lines:
                    setattr(sub.mpls_attribute.first(), k, to_update.get(k))
            elif 'interconnect' in k:
                interconnect.append(k)
            else:
                setattr(the_mpls, k, to_update.get(k))

        if interconnect:
            if not the_mpls.mpls_interconnect_ip:
                new_group = IPGroup(group_name=f'for {l.line_code} {the_mpls.vrf}')
                db.session.add(new_group)
                the_mpls.mpls_interconnect_ip = new_group

            required_key = ('interconnect_client',
                            'interconnect_netmask',
                            'interconnect_pe')

            required_key_map = {'interconnect_client': 'IP',
                                'interconnect_netmask': 'netmask',
                                'interconnect_pe': 'gateway'}
            for r in required_key:
                if r not in interconnect:
                    if the_mpls.mpls_interconnect_ip.ip_list.first():
                        to_update[r] = getattr(the_mpls.mpls_interconnect_ip.ip_list.first(), required_key_map[r])

            vr = verify_required(
                **{k: to_update.get(k) for k in required_key})
            if vr is not True:
                return vr

            vn = verify_network(**{'IP': to_update.get('interconnect_client'),
                                   'netmask': to_update.get('interconnect_netmask'),
                                   'gateway': to_update.get('interconnect_pe')})
            if vn is not True:
                return vn

            for k in required_key:
                setattr(the_mpls.mpls_interconnect_ip.ip_list.first(), required_key_map[k], to_update.get(k))

    dia_attribute_update_key = {'interconnection_supplier', 'interconnection_us', 'interconnection_netmask'} & set(
        to_update.keys())

    map_dict = {'interconnection_us': 'IP',
                'interconnection_supplier': 'gateway',
                'interconnection_netmask': 'netmask'}

    if dia_attribute_update_key:
        the_dia = l.dia_attribute.all()
        r = verify_required(interconnection_supplier=to_update.get('interconnection_supplier'),
                            interconnection_us=to_update.get('interconnection_us'),
                            interconnection_netmask=to_update.get('interconnection_netmask'))
        if r is not True:
            return r
        else:
            r = verify_network(**{map_dict[k]: to_update.get(k) for k in dia_attribute_update_key})
            if r is not True:
                return r
            new_ip = new_data_obj('IPManager',
                                  **{"IP": to_update.get('interconnection_us'),
                                     "netmask": to_update.get('interconnection_netmask'),
                                     "gateway": to_update.get('interconnection_supplier')})
            db.session.add(new_ip)
            the_dia[0].isp_ip = new_ip

    if "line_desc" in to_update.keys():
        l.line_desc = to_update['line_desc']

    if 'protect' in to_update.keys():
        pd = {'是': 1, '否': 0}
        l.protect = pd[to_update['protect']]

    if 'cloud_provider' in to_update.keys() and 'cloud_accesspoint' in to_update.keys() and l.product_model.upper() in [
        "SDWAN", "DCA"]:
        if not l.cloud_attribute.first():
            new_cloud = Cloud()
            new_cloud.cloud_provider = to_update['cloud_provider']
            new_cloud.cloud_accesspoint = to_update['cloud_accesspoint']
            new_cloud.line_cloud = l
            db.session.add(new_cloud)
            db.session.commit()
        l.cloud_attribute.first().cloud_provider = to_update['cloud_provider']

    if len({'cloud_provider', 'cloud_accesspoint'} & set(to_update.keys())) == 1:
        return {
            "fieldErrors": [
                {
                    "name": list({'cloud_provider', 'cloud_accesspoint'} - (
                            {'cloud_provider', 'cloud_accesspoint'} & set(to_update.keys())))[0],
                    "status": "必填"
                }
            ]
        }

    # 城网路由更新
    man_map = {"a_a_man": "a_a_chain_man", "a_z_man": "a_z_chain_man", "a_man": "a_a-z_man",
               "z_a_man": "z_a_chain_man", "z_z_man": "z_z_chain_man", "z_man": "z_a-z_man"}
    man_chain_map = {"a_man": ["a_a_man", "a_z_man"], "z_man": ["z_a_man", "z_z_man"]}

    for man in ('a_man', 'z_man'):
        if man in to_update.keys():
            man_pop = re.split(r'—K\d+→', to_update.get(man))
            a_flag = 0
            z_flag = 0
            a_chain = man_chain_map[man][0]
            z_chain = man_chain_map[man][1]
            if a_chain in to_update.keys():
                last_a = re.split(r'—K\d+→', to_update.get(a_chain))[-1]
                a_flag = chain_add_validate(last_a, man_pop[0])
            elif getattr(l, a_chain):
                if session[man_map[a_chain]] and getattr(l, a_chain) in session[man_map[a_chain]]:
                    last_a = re.split(r'—K\d+→', getattr(l, a_chain))[-1]
                    a_flag = chain_add_validate(last_a, man_pop[0])
                elif not session[man_map[a_chain]]:
                    setattr(l, a_chain, '')

            if z_chain in to_update.keys():
                first_z = re.split(r'—K\d+→', to_update.get(z_chain))[0]
                z_flag = chain_add_validate(first_z, man_pop[-1])
            elif getattr(l, z_chain):
                if session[man_map[z_chain]] and getattr(l, z_chain) in session[man_map[z_chain]]:
                    first_z = re.split(r'—K\d+→', getattr(l, z_chain))[0]
                    z_flag = chain_add_validate(first_z, man_pop[-1])
                elif not session[man_map[a_chain]]:
                    l.z_chain = ''
                    l.z_e = ''

            if a_flag != 2 and z_flag != 2:
                if a_flag == 1:
                    if a_chain in to_update.keys():
                        setattr(l, a_chain, to_update[a_chain])
                if z_flag == 1:
                    if z_chain in to_update.keys():
                        setattr(l, z_chain, to_update[z_chain])
                setattr(l, man, to_update[man])
                # verify_ring(l)
            elif a_flag == 2 or z_flag == 2:
                return {'error': '选路错误，无法衔接'}

    chain2man = {"a_a_man": "a_man", "a_z_man": "a_man", "z_a_man": "z_man", "z_z_man": "z_man"}

    for man_chain in ("a_a_man", "z_a_man"):
        if man_chain in to_update.keys() and chain2man[man_chain] not in to_update.keys():
            if getattr(l, chain2man[man_chain]):
                a_flag = chain_add_validate(re.split(r'—K\d+→', to_update.get('a_chain'))[-1],
                                            re.split(r'—K\d+→', l.main_route)[0])
            else:
                a_flag = 1
            if a_flag == 1:
                setattr(l, man_chain, to_update[man_chain])
            elif a_flag == 2:
                return {
                    "fieldErrors": [
                        {
                            "name": "a_chain",
                            "status": "路由选择错误，不可与主路由衔接"
                        }
                    ]
                }

    for man_chain in ("a_z_man", "z_z_man"):
        if man_chain in to_update.keys() and chain2man[man_chain] not in to_update.keys():
            if getattr(l, chain2man[man_chain]):
                z_flag = chain_add_validate(re.split(r'—K\d+→', to_update.get(man_chain))[0],
                                            re.split(r'—K\d+→', getattr(l, chain2man[man_chain]))[-1])
            else:
                z_flag = 1
            if z_flag == 1:
                setattr(l, man_chain, to_update[man_chain])
            elif z_flag == 2:
                return {
                    "fieldErrors": [
                        {
                            "name": "a_chain",
                            "status": "路由选择错误，不可与主路由衔接"
                        }
                    ]
                }

    # route update
    if 'main_route' in to_update.keys():
        main_pop = re.split(r'\W.*?', to_update.get('main_route'))
        a_flag = 0
        z_flag = 0
        if 'a_chain' in to_update.keys():
            last_a = re.split(r'\W.*?', to_update.get('a_chain'))[-1]
            a_flag = chain_add_validate(last_a, main_pop[0])
        elif l.a_chain:
            print('a chain route ', session.get('a_chain_routes'))
            if session['a_chain_routes'] and l.a_chain in session['a_chain_routes']:
                last_a = re.split(r'\W.*?', l.a_chain)[-1]
                a_flag = chain_add_validate(last_a, main_pop[0])
            elif not session['a_chain_routes']:
                l.a_chain = ''
                l.a_e = ''

        if 'z_chain' in to_update.keys():
            first_z = re.split(r'\W.*?', to_update.get('z_chain'))[0]
            z_flag = chain_add_validate(first_z, main_pop[-1])
        elif l.z_chain:
            if session['z_chain_routes'] and l.z_chain in session['z_chain_routes']:
                first_z = re.split(r'\W.*?', l.z_chain)[0]
                z_flag = chain_add_validate(first_z, main_pop[-1])
            elif not session['z_chain_routes']:
                l.z_chain = ''
                l.z_e = ''

        if a_flag != 2 and z_flag != 2:
            if a_flag == 1:
                l.a_chain = to_update['a_chain']
                l.a_e = session['a_chain-e'][session['a_chain_routes'].index(to_update['a_chain'])]
            if z_flag == 1:
                l.z_chain = to_update['z_chain']
                l.z_e = session['z_chain-e'][session['z_chain_routes'].index(to_update['z_chain'])]
            l.main_route = to_update['main_route']
            main_e_dict = session['a_z-e'][session['a_z_routes'].index(to_update['main_route'])]
            verify_ring(l)
            logger.debug(f'main route is {main_e_dict}')
            for value in main_e_dict.values():
                l.main_e = value
        elif a_flag == 2 or z_flag == 2:
            return {'error': '选路错误，无法衔接'}
    # route update
    if 'a_chain' in to_update.keys() and 'main_route' not in to_update.keys():
        if l.main_route:
            a_flag = chain_add_validate(re.split(r'\W.*?', to_update.get('a_chain'))[-1],
                                        re.split(r'\W.*?', l.main_route)[0])
        else:
            return {
                "fieldErrors": [
                    {
                        "name": "main_route",
                        "status": "主路由必选"
                    }
                ]
            }
        if a_flag == 1:
            l.a_chain = to_update['a_chain']
            l.a_e = session['a_chain-e'][session['a_chain_routes'].index(to_update['a_chain'])]
            for value in session['a_z-e'][session['a_z_routes'].index(l.main_route)].values():
                l.main_e = value
        elif a_flag == 2:
            return {
                "fieldErrors": [
                    {
                        "name": "a_chain",
                        "status": "路由选择错误，不可与主路由衔接"
                    }
                ]
            }
    # route update
    if 'z_chain' in to_update.keys() and 'main_route' not in to_update.keys():
        if l.main_route:
            z_flag = chain_add_validate(re.split(r'\W.*?', to_update.get('z_chain'))[0],
                                        re.split(r'\W.*?', l.main_route)[-1])
        else:
            return {
                "fieldErrors": [
                    {
                        "name": "main_route",
                        "status": "主路由必选"
                    }
                ]
            }
        if z_flag == 1:
            l.z_chain = to_update['z_chain']
            l.z_e = session['z_chain-e'][session['z_chain_routes'].index(to_update['z_chain'])]
            for value in session['a_z-e'][session['a_z_routes'].index(l.main_route)].values():
                l.main_e = value
        elif z_flag == 2:
            return {
                "fieldErrors": [
                    {
                        "name": "a_chain",
                        "status": "路由选择错误，不可与主路由衔接"
                    }
                ]
            }

    # interface update
    if 'a_pop_interface_id' in to_update.keys():
        if not l.a_pop_interface or (
                l.a_pop_interface and l.a_interface.device_interface.machine_room.cities.city != Interfaces.query.get(
            to_update['a_pop_interface_id']).device_interface.machine_room.cities.city):
            verify_ring_flag = True
        l.a_pop_interface = to_update['a_pop_interface_id']
    # interface update
    if 'z_pop_interface_id' in to_update.keys():
        if not l.z_pop_interface or (
                l.a_pop_interface and l.z_interface.device_interface.machine_room.cities.city != Interfaces.query.get(
            to_update['z_pop_interface_id']).device_interface.machine_room.cities.city):
            verify_ring_flag = True
        l.z_pop_interface = to_update['z_pop_interface_id']

    # backbone domain update
    if 'domains' in to_update.keys() and to_update['domains']:
        platform_id = to_update.get('platform_id', l.platform)
        if l.domains:
            logger.debug(f"The domains now are {l.domains}")
            l.domains = []
            db.session.commit()

        if 'ERPS' in to_update['domains']:
            new_d = new_data_obj("Domains", **{"name": to_update['domains'], "platform": platform_id})
            l.domains.append(new_d)

        else:
            _d = to_update['domains'].split('_')
            for dm in _d:
                new_d = new_data_obj("Domains", **{"name": dm, "platform": platform_id})
                l.domains.append(new_d)
        verify_ring_flag = True

    if 'have_a_man' in to_update.keys() and to_update.get("have_a_man") == '0':
        logger.debug(f"The MAN domains now are {l.domains}, delete the MAN domains and platform")
        l.MAN_domains_a = []
        l.MAN_platform_a = None
        db.session.commit()

    if 'have_z_man' in to_update.keys() and to_update.get("have_z_man") == '0':
        logger.debug(f"The MAN domains now are {l.domains}, delete the MAN domains and platform")
        l.MAN_domains_z = []
        l.MAN_platform_z = None
        db.session.commit()

    # Z MAN domain update
    if 'z_man_domains' in to_update.keys() and to_update['z_man_domains']:
        platform_id = to_update.get('z_man_platform_id', l.MAN_platform_z)
        # clear domains
        if l.MAN_domains_z:
            logger.debug(f"The MAN domains now are {l.MAN_domains_z}")
            l.MAN_domains_z = []
            db.session.commit()

        _d = to_update['z_man_domains'].split('_')
        for dm in _d:
            new_d = new_data_obj("Domains", **{"name": dm, "platform": platform_id})
            l.MAN_domains_z.append(new_d)
        verify_ring_flag = True

    # A MAN domain update
    if 'a_man_domains' in to_update.keys() and to_update['a_man_domains']:
        platform_id = to_update.get('a_man_platform_id', l.MAN_platform_a)
        # clear domains
        if l.MAN_domains_a:
            logger.debug(f"The MAN domains now are {l.MAN_domains_a}")
            l.MAN_domains_a = []
            db.session.commit()

        _d = to_update['a_man_domains'].split('_')
        for dm in _d:
            new_d = new_data_obj("Domains", **{"name": dm, "platform": platform_id})
            l.MAN_domains_a.append(new_d)
        verify_ring_flag = True

    # platform update
    if 'platform_id' in to_update.keys() and to_update['platform_id']:
        l.platform = to_update['platform_id']
        verify_ring_flag = True

    elif 'platform_id' in to_update.keys() and not to_update['platform_id']:
        l.platform = None
        if l.domains:
            logger.debug(f"The domains now are {l.domains}")
            l.domains = []
            db.session.commit()

    # a MAN platform update
    if 'a_man_platform_id' in to_update.keys() and to_update['a_man_platform_id']:
        l.MAN_platform_a = to_update['a_man_platform_id']
        verify_ring_flag = True

    # z MAN platform update
    if 'z_man_platform_id' in to_update.keys() and to_update['z_man_platform_id']:
        l.MAN_platform_z = to_update['z_man_platform_id']
        verify_ring_flag = True

    # update vlan description
    if 'vlan_desc' in to_update.keys():
        l.vlans.desc = to_update['vlan_desc']

    # vlan update
    if 'vlan_type' in to_update.keys():
        logger.debug('changing vlan type')
        vtype = to_update['vlan_type']
        if l.vlans and l.vlans.type == vtype:
            pass
        else:
            if vtype == 'access' or vtype == 'trunk':
                op_result = __op_vlan(line=l, vlan_class='vlan', vlan_type=vtype)
                if isinstance(op_result, dict):
                    db.session.rollback()
                    return op_result
                if op_result is True:
                    verify_ring_flag = True
                    db.session.commit()

            if vtype == 'vxlan':
                op_result_bd = __op_vlan(line=l, vlan_class='vlan', vlan_type=vtype)
                if isinstance(op_result_bd, dict):
                    db.session.rollback()
                    return op_result_bd

                op_result_vxlan = __op_vlan(line=l, vlan_class='vxlan_inside', vlan_type=vtype)
                if isinstance(op_result_vxlan, dict):
                    db.session.rollback()
                    return op_result_vxlan
                if op_result_vxlan is True:
                    verify_ring_flag = True
                    db.session.commit()

                if op_result_bd is True and op_result_vxlan is True:
                    verify_ring_flag = True
                    db.session.commit()
                elif op_result_bd is not True or op_result_vxlan is not True:
                    db.session.rollback()

            if vtype == 'qinq':
                op_result1 = __op_vlan(line=l, vlan_class='vlan', vlan_type=vtype)
                if isinstance(op_result1, dict):
                    db.session.rollback()
                    return op_result1

                op_result2 = __op_vlan(l, 'qinq_inside', vtype)
                if isinstance(op_result2, dict):
                    db.session.rollback()
                    return op_result2

                if op_result1 is True and op_result2 is True:
                    verify_ring_flag = True
                    db.session.commit()
                elif op_result1 is not True or op_result2 is not True:
                    db.session.rollback()

            if vtype == 'vlan_map':
                op_result3 = __op_vlan(line=l, vlan_class='vlan', vlan_type=vtype)
                if isinstance(op_result3, dict):
                    db.session.rollback()
                    return op_result3

                op_result4 = __op_vlan(l, 'vlan_map_to', vtype)
                if isinstance(op_result4, dict):
                    db.session.rollback()
                    return op_result4

                if op_result3 is True and op_result4 is True:
                    verify_ring_flag = True
                    db.session.commit()
                elif op_result3 is not True or op_result4 is not True:
                    db.session.rollback()

    # vlan update
    if {'vlan', 'qinq_inside', 'vlan_map_to', 'vxlan_inside'} & set(
            to_update.keys()) and 'vlan_type' not in to_update.keys():
        if not l.vlans:
            if l.product_model == 'VXLAN':
                r1 = __op_vlan(l, 'vlan', 'vxlan')
                if isinstance(r1, dict):
                    db.session.rollback()
                    return r1

                r2 = __op_vlan(l, 'vxlan_inside', 'vxlan')
                if isinstance(r2, dict):
                    db.session.rollback()
                    return r2

                if r1 is True and r2 is True:
                    verify_ring_flag = True
                    db.session.commit()
                elif r1 is not True or r2 is not True:
                    db.session.rollback()
            else:
                r1 = __op_vlan(l, 'vlan', 'access')
                if isinstance(r1, dict):
                    db.session.rollback()
                    return r1
                if r1 is True:
                    verify_ring_flag = True
                    db.session.commit()

        elif l.vlans:
            if l.vlans.type in ('access', 'trunk'):
                if l.product_model == 'VXLAN':
                    r1 = __op_vlan(l, 'vlan', 'vxlan')
                    if isinstance(r1, dict):
                        db.session.rollback()
                        return r1

                    r2 = __op_vlan(l, 'vxlan_inside', 'vxlan')
                    if isinstance(r2, dict):
                        db.session.rollback()
                        return r2

                    if r1 is True and r2 is True:
                        verify_ring_flag = True
                        db.session.commit()
                    elif r1 is not True or r2 is not True:
                        db.session.rollback()
                else:
                    r1 = __op_vlan(l, 'vlan', l.vlans.type)
                    if isinstance(r1, dict):
                        db.session.rollback()
                        return r1
                    if r1 is True:
                        verify_ring_flag = True
                        db.session.commit()
            elif l.vlans.type in ('qinq', 'vxlan'):
                op_result1 = __op_vlan(line=l, vlan_class='vlan', vlan_type=l.vlans.type)
                if isinstance(op_result1, dict):
                    db.session.rollback()
                    return op_result1

                op_result2 = __op_vlan(l, 'qinq_inside' if l.vlans.type == 'qinq' else 'vxlan_inside', l.vlans.type)
                if isinstance(op_result2, dict):
                    db.session.rollback()
                    return op_result2

                if op_result1 is True and op_result2 is True:
                    verify_ring_flag = True
                    db.session.commit()
                elif op_result1 is not True or op_result2 is not True:
                    db.session.rollback()
            elif l.vlans.type == 'vlan_map':
                op_result3 = __op_vlan(line=l, vlan_class='vlan', vlan_type='vlan_map')
                if isinstance(op_result3, dict):
                    db.session.rollback()
                    return op_result3

                op_result4 = __op_vlan(l, 'vlan_map_to', 'vlan_map')
                if isinstance(op_result4, dict):
                    db.session.rollback()
                    return op_result4

                if op_result3 is True and op_result4 is True:
                    verify_ring_flag = True
                    db.session.commit()
                elif op_result3 is not True or op_result4 is not True:
                    db.session.rollback()

    # 更新操作人、操作时间
    if not l.operator:
        l.line_operator = session['SELFID']
        l.operate_time = datetime.datetime.now()

    try:
        db.session.add(l)
        db.session.commit()
        # 验证环配置，目前仅检测93平台
        if verify_ring_flag:
            verify_ring(l)
        if l.product_model.upper() == 'MPLS':
            if {'vrf', 'rt'} & set(to_update.keys()):
                return make_table_mpls(LineDataBank.query.filter_by(line_code=l.line_code).all())
            else:
                return make_table_mpls([l])
        elif l.product_model.upper() == 'VXLAN':
            return make_table_vxlan([l])
        elif l.product_model.upper() == 'DIA':
            return make_table_dia([l])
        else:
            return make_table([l])
    except Exception as e:
        logger.error(f'editor error for {e}')
        db.session.rollback()
        return {'error': '数据库提交失败'}


def remove(data):
    logger.info(str(data) + ' to be deleted')
    try:
        for row_id, value in data.items():
            _id = row_id.split('_')[1]
            to_be_delete = LineDataBank.query.get(_id)
            to_be_delete.record_status = 998
            db.session.commit()
        return {}
    except Exception as e:
        return {'error': e}


def __remove_ip(data):
    logger.info(str(data) + ' to be deleted')
    try:
        for row_id, value in data.items():
            _id = row_id.split('_')[1]
            to_be_delete = IPManager.query.get(_id)
            db.session.delete(to_be_delete)
            db.session.commit()
        return {}
    except Exception as e:
        return {'error': e}


def remove_dia_ip(data):
    return __remove_ip(data)


def remove_mpls_route(data):
    return __remove_ip(data)


def remove_supplier_ip(data):
    return __remove_ip(data)
