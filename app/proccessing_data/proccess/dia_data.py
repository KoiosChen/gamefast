from ... import db, logger
from ...models import LineDataBank, IPSupplier, IPManager, IPGroup, DIA
from ...proccessing_data.get_datatable import make_table, make_table_ip_supplier, make_table_supplier_ip, make_table_ip
from ...validate.verify_fields import verify_fields, verify_required, verify_network, verify_net_in_net
import re
from .public_methods import new_data_obj, new_linecode


def dia_ip_new(contents, line_obj):
    logger.debug(contents)
    import ipaddress
    if not contents.get('site'):
        return {'error': '未选择线路'}
    line_id = contents.get('site').split('_')[1]
    line = LineDataBank.query.get(line_id)
    dia = line.dia_attribute.first()
    contents['IP'] = contents.get('ip')
    supplier = IPSupplier.query.get(int(contents.get('supplier_id')))
    parent_ip = IPManager.query.get(int(contents.get('ip_address')))
    try:
        parent_network = ipaddress.ip_network(parent_ip.IP + '/' + parent_ip.netmask, strict=False)
    except Exception as e:
        return {'error': '供应商IP段信息缺失'}
    used_ips = parent_ip.children
    line_attr = {'IP', 'netmask', 'gateway', 'dns', 'isp', 'desc', 'available_ip'}
    updated_attr = set(contents.keys()) & line_attr
    ip_group = dia.available_dia_ip

    if contents.get('dns'):
        try:
            ipaddress.ip_address(contents.get('dns'))
            dns_ = new_data_obj('DNSManager', **{'dns': contents.get('dns')})
        except ValueError:
            logger.error(f'DNS IP format error {contents.get("dns")}')
            return {'fieldErrors': [{'name': 'dns', 'status': 'DNS 格式错误'}]}

    if contents.get('netmask'):
        vf = verify_fields('netmask', 'netmask', contents.get('netmask'))
        if vf is not True:
            return vf

    try:
        vr = verify_required(**{'ip': contents.get('ip'), 'netmask': contents.get('netmask')})
        if vr is not True:
            return vr
        ip_network = ipaddress.ip_network(contents['ip'] + '/' + contents['netmask'], strict=False)
    except ValueError:
        return {'error': "格式错误"}

    if not line_obj:
        # 供应商为路由模式，dia需要是网关、路由或者NAT模式（1，2，4）
        if supplier.mode == 2:
            # dia网关模式，验证互联地址为供应商地址段，dia 的ip group中添加的，可认为是secondary地址，也就是第二个互联地址
            if dia.mode == 1:
                vr = verify_required(**{'gateway': contents.get('gateway')})
                if vr is not True:
                    return vr
                else:
                    try:
                        vn = verify_network(**{'IP': contents.get('ip'),
                                               'netmask': contents.get('netmask'),
                                               'gateway': contents.get('gateway')})
                        if vn is not True:
                            return vn

                        vn_in_supplier = verify_net_in_net(
                            **{'source_net': contents.get('ip') + '/' + contents.get('netmask'),
                               'target_net': parent_ip.IP + '/' + parent_ip.netmask})
                        if vn_in_supplier is not True:
                            return vn_in_supplier

                    except ValueError:
                        return {'error': 'IP地址段不符合'}
            elif dia.mode == 2:
                if vr is not True:
                    return vr
                else:
                    try:
                        vn_in_supplier = verify_net_in_net(
                            **{'source_net': contents.get('ip') + '/' + contents.get('netmask'),
                               'target_net': parent_ip.IP + '/' + parent_ip.netmask})
                        if vn_in_supplier is not True:
                            return vn_in_supplier
                    except ValueError:
                        return {'error': 'IP地址段不符合'}
            elif dia.mode == 3:
                return {'error': '供应商为路由模式，与客户互联不可为透传模式'}
            elif dia.mode == 4:
                pass
        else:
            if dia.mode == 3:
                vr = verify_required(**{'gateway': contents.get('gateway')})
                if vr is not True:
                    return vr

                try:
                    vn = verify_network(**{'IP': contents.get('ip'), 'netmask': contents.get('netmask'),
                                           'gateway': contents.get('gateway')})
                    if vn is not True:
                        return vn

                    vn_in_supplier = verify_net_in_net(
                        **{'source_net': contents.get('ip') + '/' + contents.get('netmask'),
                           'target_net': parent_ip.IP + '/' + parent_ip.netmask})
                    if vn_in_supplier is not True:
                        return vn_in_supplier

                except Exception as e:
                    logger.error(e)
                    return {'error': 'IP地址段不符合'}

            elif dia.mode == 4:
                if vr is not True:
                    return vr

                if int(contents.get('netmask')) != 32:
                    return {'error': 'NAT模式掩码必须为32'}

                try:
                    vn = verify_network(**{'IP': contents.get('ip'), 'netmask': contents.get('netmask'),
                                           'gateway': contents.get('gateway')})
                    if vn is not True:
                        return vn

                    vn_in_supplier = verify_net_in_net(
                        **{'source_net': contents.get('ip') + '/' + contents.get('netmask'),
                           'target_net': parent_ip.IP + '/' + parent_ip.netmask})
                    if vn_in_supplier is not True:
                        return vn_in_supplier

                except Exception as e:
                    logger.error(e)
                    return {'error': 'IP或掩码格式错误'}
            else:
                return {'error': "模式不匹配"}

        if not ip_group:
            ip_group = IPGroup(group_name=f'For line-dia {line.line_code}')
            db.session.add(ip_group)

        new_ip = new_data_obj('IPManager',
                              **{'IP': contents['ip'],
                                 'netmask': contents['netmask'],
                                 'desc': f"For supplier {supplier.line_code}",
                                 'gateway': contents.get('gateway'),
                                 'available_ip': contents.get('available_ip') if contents.get('available_ip') else str(
                                     ip_network[1]) + '-' + str(ip_network[-2]),
                                 'isp': contents.get('isp', '')})

        new_ip.parent_id = parent_ip.id
        if contents.get('dns'):
            new_ip.ip_dns = dns_

        new_ip.group = ip_group

        dia.available_dia_ip = ip_group
        db.session.add(dia)
        db.session.add(supplier)
        db.session.commit()
    return {'data': make_table_ip([new_ip])}


def dia_ip_update(contents, line_obj):
    logger.debug(f'in dia ip update {contents}')
    from IPy import IP
    net = IP(line_obj.IP + '/' + line_obj.netmask, make_net=True)
    for k, v in contents.items():
        if k == 'available_ip' and v:
            value = v.replace('，', ',')
            ips = re.split(r',|，', value)
            print(ips)
            for ip in ips:
                ip = ip.strip()
                print('ip is ', ip)
                if '-' in ip:
                    ip1, ip2 = re.split('-', ip)
                    try:
                        ip1 = IP(ip1.strip())
                        ip2 = IP(ip2.strip())
                        if not (ip1 in net and ip2 in net and ip1 <= ip2):
                            return {'error': '可用IP地址范围错误'}
                    except ValueError:
                        return {'fieldErrors': [{'name': 'available_ip', 'status': 'IP地址格式错误'}]}
                else:
                    try:
                        if not (IP(ip.strip())) in net:
                            return {'error': '可用IP地址范围错误'}
                    except ValueError:
                        return {'fieldErrors': [{'name': 'available_ip', 'status': 'IP地址格式错误'}]}
                setattr(line_obj, 'available_ip', v)
        if k == 'dns' and v:
            try:
                IP(v)
                setattr(line_obj.ip_dns, 'dns', v)
            except ValueError:
                return {'fieldErrors': [{'name': 'dns', 'status': 'dns格式错误'}]}
    return {'data': make_table_ip([line_obj])}
