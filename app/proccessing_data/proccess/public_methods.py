from ... import db, logger
from flask import jsonify, session
from ...models import LineDataBank, Domains, Customer, MachineRoom, Vlan, Contacts, User, Interfaces, Cloud, VXLAN, \
    IPSupplier, IPManager, IPGroup, DNSManager, DIA, City
from ...proccessing_data.get_datatable import make_table, make_table_ip_supplier, make_table_supplier_ip, make_table_ip
from ...validate.verify_fields import verify_fields, chain_add_validate, verify_required, verify_network, \
    verify_net_in_net
import re
import datetime
import os


def save_xlsx(file, file_path, session_name):
    f = file  # 获取文件对象
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    complete_filename = os.path.join(file_path, new_linecode() + '.xlsx')
    f.save(complete_filename)
    session[session_name] = complete_filename
    f.close()
    return complete_filename


def new_data_obj(table, **kwargs):
    """
    创建新的数据对象
    :param table: 表名
    :param kwargs: 表数据，需要对应表字段
    :return: 新增，或者已有数据的对象
    """
    logger.debug(f">>> Check the {table} for data {kwargs}")
    __obj = eval(table).query.filter_by(**kwargs).first()
    if not __obj:
        logger.debug(f">>> The table {table} does not have the obj, create new one!")
        try:
            __obj = eval(table)(**kwargs)
            db.session.add(__obj)
            db.session.commit()
        except Exception as e:
            logger.error(f'create {table} fail {kwargs} {e}')
            db.session.rollback()
            return False
    else:
        logger.debug(f">>> The line exist in {table} for {kwargs}")
    return __obj


def new_linecode():
    """
    生成唯一的线路表的ID
    :return:
    """
    nowtime = datetime.datetime.now()
    year = str(nowtime.year)
    month = str(nowtime.month).zfill(2)
    day = str(nowtime.day).zfill(2)
    hour = str(nowtime.hour).zfill(2)
    minute = str(nowtime.minute).zfill(2)
    second = str(nowtime.second).zfill(2)
    return ''.join([year, month, day, hour, minute, second])


def operate_vlans(vlan_line, vlan_class, vlan_type, update_info):
    """
    用于vlan数据的修改
    :param vlan_line:
    :param vlan_class: it's a list
    :param vlan_type:
    :param update_info:
    :return:
    """
    return_result = {'fieldErrors': []}

    for vc in vlan_class:
        if vc == 'vlan':
            if vc in update_info.keys():
                v = verify_fields('vlan', vc, update_info.get(vc), vlan_type)
                if v is not True:
                    return_result['fieldErrors'].extend(v['fieldErrors'])
                    break
                if vlan_line and vlan_line.name == update_info.get(vc):
                    for c in vlan_line.children:
                        db.session.delete(c)
                    vlan_line.type = vlan_type

                elif (vlan_line and vlan_line.name != update_info.get(vc)) or not vlan_line:
                    new_vlan = Vlan(name=update_info.get(vc), type=vlan_type)

                    old_children = list()
                    if vlan_line and vlan_line.children:
                        old_children = vlan_line.children

                    db.session.add(new_vlan)

                    vlan_line = new_vlan

                    if old_children:
                        for oc in old_children:
                            vlan_line.children.append(oc)

            elif vc not in update_info.keys() and vlan_line:
                if re.search(r'\D+', vlan_line.name) and vlan_type in ('access', 'vxlan'):
                    return_result['fieldErrors'].append({"name": vc, "status": "非法字符"})
                    break
                vlan_line.type = vlan_type
                for c in vlan_line.children:
                    db.session.delete(c)
            else:
                return_result['error'] = "Vlan错误，请重新选择"
                break

        elif vc in ('qinq_inside', 'vxlan_inside', 'vlan_map_to'):
            if vc in update_info.keys():
                if vc == 'vlan_map_to':
                    if re.search(r'\D+', update_info.get(vc)):
                        return_result['fieldErrors'].append({"name": vc, "status": "仅数值（1-4096）"})
                        break
                value = update_info.get(vc).replace('，', ',')
                v = verify_fields('vlan', vc, value)
                if isinstance(v, dict):
                    return_result['fieldErrors'].extend(v['fieldErrors'])
                    break

                if vlan_line and ((vlan_line.children and value not in vlan_line.children) or not vlan_line.children):
                    for c in vlan_line.children:
                        db.session.delete(c)
                    new_vlan = Vlan(name=value, type=vc)
                    db.session.add(new_vlan)
                    vlan_line.children.append(new_vlan)
                elif not vlan_line:
                    return_result['error'] = '缺少 {} Vlan'.format(vlan_type)
                    break
            elif vc not in update_info.keys() and vlan_line and vlan_line.children:
                for c in vlan_line.children:
                    c.type = vc
            elif vc not in update_info.keys() and (not vlan_line or (vlan_line and not vlan_line.children)):
                return_result['error'] = '缺少必要Vlan'
                break

    return {'status': True, 'data': vlan_line} if not return_result['fieldErrors'] and not return_result.get(
        'error') else {'status': False, 'data': return_result}


def contacts_update(l, to_update, attr_prefix=None):
    """

    :param l: 要更新的记录对象
    :param to_update: 更新数据的字典
    :param attr_prefix:
    :return:
    """
    contacts = {'biz_contact_name', 'noc_contact_name', 'customer_manager_name', 'biz_contact_phoneNumber',
                'biz_contact_email', 'noc_contact_phoneNumber', 'noc_contact_email', 'customer_manager_phoneNumber'}

    contacts_to_update = contacts & set(to_update.keys())

    # contacts update
    if contacts_to_update:
        for contact in contacts_to_update:
            if 'name' in contact:
                name_v = verify_fields('name', contact, to_update.get(contact))
                if isinstance(name_v, dict):
                    return name_v
            elif 'email' in contact:
                email_v = verify_fields('email', contact, to_update.get(contact))
                if isinstance(email_v, dict):
                    return email_v
            elif 'phone' in contact:
                phone_v = verify_fields('phone', contact, to_update.get(contact))
                if isinstance(phone_v, dict):
                    return phone_v

            contact_attr = '_'.join(contact.split('_')[:2]) if 'customer' not in contact else '_'.join(
                contact.split('_')[:2]) + '_contact'

            contact_field = contact.split('_')[-1]

            if attr_prefix is not None:
                contact_attr = attr_prefix + '_' + contact_attr

            if hasattr(l, contact_attr) and getattr(l, contact_attr):
                now_contact = getattr(l, contact_attr)
                setattr(now_contact, contact_field, to_update.get(contact))
            elif hasattr(l, contact_attr) and not getattr(l, contact_attr):
                new_contact = Contacts()

                setattr(new_contact, contact_field, to_update.get(contact))

                setattr(l, contact_attr, new_contact)

                db.session.add(new_contact)
                db.session.add(l)
        return True


def vlan_update(vlan_obj, to_update):
    # update vlan description
    if 'vlan_desc' in to_update.keys():
        if vlan_obj:
            vlan_obj.desc = to_update['vlan_desc']
            return {'status': True, 'data': vlan_obj}
        else:
            return {'status': False, 'data': {'error': 'vlan不存在，请先创建vlan后再填写vlan描述'}}

    # vlan update
    if 'vlan_type' in to_update.keys():
        logger.debug('changing vlan type')
        vtype = to_update['vlan_type']
        if vlan_obj and vlan_obj.type == vtype:
            return {'error': 'vlan type change error'}
        else:
            if vtype in ('access', 'trunk'):
                op_result = operate_vlans(vlan_obj, ['vlan'], vtype, to_update)
            elif vtype == 'qinq':
                op_result = operate_vlans(vlan_obj, ['vlan', 'qinq_inside'], vtype, to_update)
            elif vtype == 'vlan_map':
                op_result = operate_vlans(vlan_obj, ['vlan', 'vlan_map_to'], vtype, to_update)
            else:
                return {'error': 'The vlan type is not exist!'}

            db.session.commit() if op_result['status'] else db.session.rollback()
            return op_result

    # vlan update
    if {'vlan', 'qinq_inside', 'vlan_map_to', 'vxlan_inside'} & set(
            to_update.keys()) and 'vlan_type' not in to_update.keys():
        if not vlan_obj:
            op_result = operate_vlans(vlan_obj, ['vlan'], 'access', to_update)
            logger.debug(f'operate result is {op_result}')
            db.session.commit() if op_result['status'] else db.session.rollback()
            return op_result

        elif vlan_obj:
            if vlan_obj.type in ('access', 'trunk'):
                op_result = operate_vlans(vlan_obj, ['vlan'], vlan_obj.type, to_update)
            elif vlan_obj.type == 'qinq':
                op_result = operate_vlans(vlan_obj, ['vlan', 'qinq_inside'], vlan_obj.type, to_update)
            elif vlan_obj.type == 'vlan_map':
                op_result = operate_vlans(vlan_obj, ['vlan', 'vlan_map_to'], vlan_obj.type, to_update)
            else:
                return {'error': 'The vlan type is not exist!'}

            db.session.commit() if op_result['status'] else db.session.rollback()
            return op_result
