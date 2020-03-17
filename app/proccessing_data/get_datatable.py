from ..models import channel_type, LineDataBank, Device, Interfaces, all_domains, multi_domains, erps_instance, \
    Platforms, MachineRoom, City, IPManager, IPGroup, IPSupplier
from sqlalchemy import or_


def make_table(lines=None, page_start=None, length=None):
    if lines is None:
        lines = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                          LineDataBank.line_status.__ne__(100),
                                          or_(LineDataBank.product_model.__eq__('DPLC'),
                                              LineDataBank.product_model.__eq__('DCA'))).order_by(
            LineDataBank.create_time.desc()).offset(page_start).limit(length)

    return [{"DT_RowId": "row_" + str(l.id),
             "customer_name": l.customer_linedata.name if l.customer_linedata.name else "",
             "line_code": l.line_code if l.line_code else "",
             "sub_line_code": l.sub_line_code if l.sub_line_code else "",
             "a_client_addr": l.a_client_addr if l.a_client_addr else "",
             "a_pop_city": l.a_interface.device_interface.machine_room.cities.city if l.a_interface else {},
             "a_pop_city_id": l.a_interface.device_interface.machine_room.cities.id if l.a_interface else {},
             "a_pop": l.a_interface.device_interface.machine_room.name if l.a_interface else "",
             "a_pop_id": l.a_interface.device_interface.machine_room.id if l.a_interface else {},
             "a_pop_device": l.a_interface.device_interface.device_name if l.a_interface else "",
             "a_pop_device_id": l.a_interface.device_interface.id if l.a_interface else {},
             "a_pop_interface": l.a_interface.interface_name if l.a_interface else "",
             "a_pop_interface_id": l.a_interface.id if l.a_interface else {},
             "a_pop_ip": l.a_interface.device_interface.ip if l.a_interface else "",
             "z_client_addr": l.z_client_addr if l.z_client_addr else "",
             "z_pop_city": l.z_interface.device_interface.machine_room.cities.city if l.z_interface else "",
             "z_pop_city_id": l.z_interface.device_interface.machine_room.cities.id if l.z_interface else {},
             "z_pop": l.z_interface.device_interface.machine_room.name if l.z_interface else "",
             "z_pop_id": l.z_interface.device_interface.machine_room.id if l.z_interface else {},
             "z_pop_device": l.z_interface.device_interface.device_name if l.z_interface else "",
             "z_pop_device_id": l.z_interface.device_interface.id if l.z_interface else {},
             "z_pop_interface": l.z_interface.interface_name if l.z_interface else "",
             "z_pop_interface_id": l.z_interface.id if l.z_interface else {},
             "z_pop_ip": l.z_interface.device_interface.ip if l.z_interface else "",
             "channel": channel_type.get(l.channel_type, 9) + ": " + str(l.channel_number) + l.channel_unit,
             "vlan": l.vlans.name if l.vlan else '',
             "vlan_desc": l.vlans.desc if l.vlan and l.vlans.desc is not None else "",
             "mode": l.dia_attribute.first().mode if l.dia_attribute.first() else "",
             "qinq_inside": ','.join(
                 [v.name for v in l.vlans.children if
                  v.type == 'qinq_inside']) if l.vlan and l.vlans.type == 'qinq' else '',
             "qinq_outside2": ','.join(
                 [v.name for v in l.vlans.children if v.type == 'multi_qinq']) if l.vlan else '',
             "vlan_map_to": ','.join(
                 [v.name for v in l.vlans.children if
                  v.type == 'vlan_map_to']) if l.vlan and l.vlans.type == 'vlan_map' else '',
             "vlan_type": l.vlans.type if l.vlans else 'access',
             "main_route": l.main_route if l.main_route else "",
             "a_chain": l.a_chain if l.a_chain else "",
             "z_chain": l.z_chain if l.z_chain else "",
             "operator": l.operator.username if l.operator else "",
             "protect": "否" if l.protect == 0 else "是",
             "biz_contact_name": l.biz_contact.name if l.biz else "",
             "biz_contact_phoneNumber": l.biz_contact.phoneNumber if l.biz else "",
             "biz_contact_email": l.biz_contact.email if l.biz else "",
             "noc_contact_name": l.noc_contact.name if l.noc else "",
             "noc_contact_phoneNumber": l.noc_contact.phoneNumber if l.noc else "",
             "noc_contact_email": l.noc_contact.email if l.noc else "",
             "customer_manager_name": l.customer_manager_contact.name if l.customer_manager else "",
             "customer_manager_phoneNumber": l.customer_manager_contact.phoneNumber if l.customer_manager else "",
             "start_date": str(l.operate_time),
             "stop_date": str(l.line_stop_time) if l.line_stop_time else "",
             "platform": l.line_platform.name if l.line_platform else "",
             "platform_id": l.line_platform.id if l.line_platform else {},
             "domains_bind": '_'.join(sorted([d.name for d in l.domains])) if l.domains else "",
             "domains": '_'.join(sorted([d.name for d in l.domains])) if l.domains else {},
             "product_type": l.product_type,
             "product_model": l.product_model,
             "validate_rrpp_status": l.validate_rrpp_status,
             "line_desc": l.line_desc if l.line_desc else "",
             "cloud_provider": l.cloud_attribute.first().cloud_provider if (
                                                                                   l.product_model.upper() == "SDWAN" or l.product_model.upper() == "DCA") and l.cloud_attribute.all() else "",
             "cloud_accesspoint": l.cloud_attribute.first().cloud_accesspoint if (
                                                                                         l.product_model.upper() == "SDWAN" or l.product_model.upper() == "DCA") and l.cloud_attribute.all() else "",
             } for l in lines]


def make_table_vxlan(lines=None):
    if lines is None:
        lines = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                          LineDataBank.line_status.__ne__(100),
                                          LineDataBank.product_model.__eq__('VXLAN')).order_by(
            LineDataBank.create_time.desc()).all()
    result = [{"DT_RowId": "row_" + str(l.id),
               "customer_name": l.customer_linedata.name,
               "line_code": l.line_code,
               "sub_line_code": l.sub_line_code if l.sub_line_code else "",
               "a_pop_city": l.a_interface.device_interface.machine_room.cities.city if l.a_interface else {},
               "a_pop_city_id": l.a_interface.device_interface.machine_room.cities.id if l.a_interface else {},
               "a_pop": l.a_interface.device_interface.machine_room.name if l.a_interface else "",
               "a_pop_id": l.a_interface.device_interface.machine_room.id if l.a_interface else {},
               "a_pop_device": l.a_interface.device_interface.device_name if l.a_interface else "",
               "a_pop_device_id": l.a_interface.device_interface.id if l.a_interface else {},
               "a_pop_interface": l.a_interface.interface_name if l.a_interface else "",
               "a_pop_interface_id": l.a_interface.id if l.a_interface else {},
               "a_pop_ip": l.a_interface.device_interface.ip if l.a_interface else "",
               "channel": channel_type[l.channel_type] + ":" + str(l.channel_number) + l.channel_unit,
               "bd": l.vxlan_attribute.all()[0].bd if l.vxlan_attribute.all() else "",
               "vlan": l.vlans.name if l.vlan else '',
               "vlan_desc": l.vlans.desc if l.vlan and l.vlans.desc is not None else "",
               "qinq_inside": ','.join(
                   [v.name for v in l.vlans.children if
                    v.type == 'qinq_inside']) if l.vlan and l.vlans.type == 'qinq' else '',
               "qinq_outside2": ','.join(
                   [v.name for v in l.vlans.children if v.type == 'multi_qinq']) if l.vlan else '',
               "vlan_map_to": ','.join(
                   [v.name for v in l.vlans.children if
                    v.type == 'vlan_map_to']) if l.vlan and l.vlans.type == 'vlan_map' else '',
               "vxlan_inside": ','.join(
                   [v.name for v in l.vlans.children if
                    v.type == 'vxlan_inside']) if l.vlan and l.vlans.type == 'vxlan' else '',
               "vlan_type": l.vlans.type if l.vlans else 'access',
               "operator": l.operator.username if l.operator else "",
               "biz_contact_name": l.biz_contact.name if l.biz else "",
               "biz_contact_phoneNumber": l.biz_contact.phoneNumber if l.biz else "",
               "biz_contact_email": l.biz_contact.email if l.biz else "",
               "noc_contact_name": l.noc_contact.name if l.noc else "",
               "noc_contact_phoneNumber": l.noc_contact.phoneNumber if l.noc else "",
               "noc_contact_email": l.noc_contact.email if l.noc else "",
               "customer_manager_name": l.customer_manager_contact.name if l.customer_manager else "",
               "customer_manager_phoneNumber": l.customer_manager_contact.phoneNumber if l.customer_manager else "",
               "start_date": str(l.operate_time),
               "stop_date": str(l.line_stop_time) if l.line_stop_time else "",
               "product_type": l.product_type,
               "product_model": l.product_model,
               "line_desc": l.line_desc if l.line_desc else "",
               "cloud_provider": l.cloud_attribute.first().cloud_provider if (l.product_model.upper() in (
                   "SDWAN", "DCA", "VXLAN")) and l.cloud_attribute.all() else "",
               "cloud_accesspoint": l.cloud_attribute.first().cloud_accesspoint if (l.product_model.upper() in (
                   "SDWAN", "DCA", "VXLAN")) and l.cloud_attribute.all() else "",
               "validate_rrpp_status": l.validate_rrpp_status
               } for l in lines]
    print(result)
    return result


def make_table_interface(lines=None):
    if lines is None:
        lines = Interfaces.query.all()
    return [{"DT_RowId": "row_" + str(l.id),
             "interface_name": l.interface_name,
             "interface_desc": l.interface_desc if l.interface_desc else "",
             "interface_type": l.interface_type if l.interface_type else "",
             "interface_status": l.interface_status if l.interface_status else ""} for l in lines]


def make_table_device(lines=None):
    if lines is None:
        lines = Device.query.all()
    return [{"DT_RowId": "row_" + str(l.id),
             "device_name": l.device_name,
             "device_ip": l.ip,
             "login_method": l.login_method if l.login_method else "",
             "login_name": l.login_name if l.login_name else "",
             "login_password": l.login_password if l.login_password else "",
             "enable_password": l.enable_password if l.enable_password else "",
             "status": "在用" if l.status else "下线",
             "status_id": l.status,
             "community": l.community,
             "monitor_status": "运行" if l.monitor_status else "离线",
             "monitor_status_id": l.monitor_status,
             "monitor_fail_date": l.monitor_fail_date,
             "monitor_rec_date": l.monitor_rec_date,
             "vendor": l.vendor,
             "device_model": l.device_model,
             "os_version": l.os_version,
             "patch_version": l.patch_version,
             "serial_number": l.serial_number,
             "device_belong": l.device_owner.name if l.device_owner else "",
             "device_belong_id": l.device_owner.id if l.device_owner else "",
             "machine_room": l.machine_room.name if l.machine_room else "",
             "machine_room_id": l.machine_room.id if l.machine_room else "",
             "platform": l.device_platform.name if l.device_platform else "",
             "platform_id": l.platform_id if l.platform_id else "",
             } for l in lines]


def make_table_machine_room(lines=None):
    level_dict = {1: "业务站", 2: "光放站"}
    type_dict = {1: "自建", 2: "缆信", 3: "第三方"}
    status_dict = {1: "在用", 0: "停用"}
    if lines is None:
        lines = MachineRoom.query.all()
    return [{"DT_RowId": "row_" + str(sc.id),
             'name': sc.name,
             'city': sc.cities.city,
             "a_pop_city_id": sc.cities.id,
             'address': sc.address,
             'level': level_dict[sc.level],
             'level_id': sc.level,
             'type': type_dict[sc.type],
             'type_id': sc.type,
             'status': status_dict[sc.status],
             'status_id': sc.status,
             'noc_contact_name': sc.administrator.name if sc.administrator and sc.administrator.name else "",
             'noc_contact_phone': sc.administrator.phoneNumber if sc.administrator and sc.administrator.phoneNumber else "",
             'noc_contact_email': sc.administrator.email if sc.administrator and sc.administrator.email else "",
             'lift': '是' if sc.lift else '否',
             'lift_id': sc.lift
             } for sc in lines]


def make_table_ip_supplier(lines=None):
    if lines is None:
        lines = IPSupplier.query.filter(IPSupplier.status.__eq__(1)).order_by(IPSupplier.create_time.desc()).all()
    result = [{"DT_RowId": "row_" + str(l.id),
               "supplier_name": l.supplier.name,
               "line_code": l.line_code,
               "a_pop_city": l.supplier_access_interface.device_interface.machine_room.cities.city if l.supplier_access_interface else {},
               "a_pop_city_id": l.supplier_access_interface.device_interface.machine_room.cities.id if l.supplier_access_interface else {},
               "a_pop": l.supplier_access_interface.device_interface.machine_room.name if l.supplier_access_interface else "",
               "a_pop_id": l.supplier_access_interface.device_interface.machine_room.id if l.supplier_access_interface else {},
               "a_pop_device": l.supplier_access_interface.device_interface.device_name if l.supplier_access_interface else "",
               "a_pop_device_id": l.supplier_access_interface.device_interface.id if l.supplier_access_interface else {},
               "a_pop_interface": l.supplier_access_interface.interface_name if l.supplier_access_interface else "",
               "a_pop_interface_id": l.supplier_access_interface.id if l.supplier_access_interface else {},
               "a_pop_ip": l.supplier_access_interface.device_interface.ip if l.supplier_access_interface else "",
               "bandwidth": str(l.bandwidth) if l.bandwidth else "",
               "bandwidth_unit": l.bandwidth_unit if l.bandwidth_unit else "",
               "vlan": l.access_vlan.name if l.vlan else '',
               "vlan_desc": l.access_vlan.desc if l.vlan and l.access_vlan.desc is not None else "",
               "qinq_inside": ','.join(
                   [v.name for v in l.access_vlan.children if
                    v.type == 'qinq_inside']) if l.vlan and l.access_vlan.type == 'qinq' else '',
               "vlan_map_to": ','.join(
                   [v.name for v in l.access_vlan.children if
                    v.type == 'vlan_map_to']) if l.vlan and l.access_vlan.type == 'vlan_map' else '',
               "vlan_type": l.access_vlan.type if l.access_vlan else 'access',
               "operator": l.supplier_operator.username if l.supplier_operator else "",
               "biz_contact_name": l.supplier_biz_contact.name if l.biz else "",
               "biz_contact_phoneNumber": l.supplier_biz_contact.phoneNumber if l.biz else "",
               "biz_contact_email": l.supplier_biz_contact.email if l.biz else "",
               "noc_contact_name": l.supplier_noc_contact.name if l.noc else "",
               "noc_contact_phoneNumber": l.supplier_noc_contact.phoneNumber if l.noc else "",
               "noc_contact_email": l.supplier_noc_contact.email if l.noc else "",
               "customer_manager_name": l.supplier_customer_manager_contact.name if l.customer_manager else "",
               "customer_manager_phoneNumber": l.supplier_customer_manager_contact.phoneNumber if l.customer_manager else "",
               "start_time": str(l.start_time),
               "stop_time": str(l.stop_time) if l.stop_time else "",
               "mode": l.mode,
               "interconnection_supplier": l.ip_a_z.gateway if l.ip_a_z else "",
               "interconnection_us": l.ip_a_z.IP if l.ip_a_z else "",
               "interconnection_netmask": l.ip_a_z.netmask if l.ip_a_z else ""
               } for l in lines]
    print(result)
    return result


def make_table_dia(lines=None):
    if lines is None:
        lines = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                          LineDataBank.line_status.__ne__(100),
                                          LineDataBank.product_model.__eq__('DIA')).order_by(
            LineDataBank.create_time.desc()).all()
    return [{"DT_RowId": "row_" + str(l.id),
             "customer_name": l.customer_linedata.name,
             "line_code": l.line_code,
             "z_client_addr": l.z_client_addr if l.z_client_addr else "",
             "z_pop_city": l.z_interface.device_interface.machine_room.cities.city if l.z_interface else "",
             "z_pop_city_id": l.z_interface.device_interface.machine_room.cities.id if l.z_interface else {},
             "z_pop": l.z_interface.device_interface.machine_room.name if l.z_interface else "",
             "z_pop_id": l.z_interface.device_interface.machine_room.id if l.z_interface else {},
             "z_pop_device": l.z_interface.device_interface.device_name if l.z_interface else "",
             "z_pop_device_id": l.z_interface.device_interface.id if l.z_interface else {},
             "z_pop_interface": l.z_interface.interface_name if l.z_interface else "",
             "z_pop_interface_id": l.z_interface.id if l.z_interface else {},
             "z_pop_ip": l.z_interface.device_interface.ip if l.z_interface else "",
             "channel": channel_type[l.channel_type] + ":" + str(l.channel_number) + l.channel_unit,
             "vlan": l.vlans.name if l.vlan else '',
             "vlan_desc": l.vlans.desc if l.vlan and l.vlans.desc is not None else "",
             "vlan_type": l.vlans.type if l.vlans else 'access',
             "operator": l.operator.username if l.operator else "",
             "biz_contact_name": l.biz_contact.name if l.biz else "",
             "biz_contact_phoneNumber": l.biz_contact.phoneNumber if l.biz else "",
             "biz_contact_email": l.biz_contact.email if l.biz else "",
             "noc_contact_name": l.noc_contact.name if l.noc else "",
             "noc_contact_phoneNumber": l.noc_contact.phoneNumber if l.noc else "",
             "noc_contact_email": l.noc_contact.email if l.noc else "",
             "customer_manager_name": l.customer_manager_contact.name if l.customer_manager else "",
             "customer_manager_phoneNumber": l.customer_manager_contact.phoneNumber if l.customer_manager else "",
             "start_date": str(l.operate_time),
             "stop_date": str(l.line_stop_time) if l.line_stop_time else "",
             "product_type": l.product_type,
             "product_model": l.product_model,
             "line_desc": l.line_desc if l.line_desc else "",
             "validate_rrpp_status": l.validate_rrpp_status,
             "mode": l.dia_attribute.first().mode if l.dia_attribute.first() else 1,
             "interconnection_supplier": l.dia_attribute.first().isp_ip.gateway if l.dia_attribute.first() and l.dia_attribute.first().isp_ip else "",
             "interconnection_us": l.dia_attribute.first().isp_ip.IP if l.dia_attribute.first() and l.dia_attribute.first().isp_ip else "",
             "interconnection_netmask": l.dia_attribute.first().isp_ip.netmask if l.dia_attribute.first() and l.dia_attribute.first().isp_ip else "",
             } for l in lines]


def make_table_ip(lines=None):
    return [{"DT_RowId": "row_" + str(line.id),
             "ip": line.IP if line.IP else "",
             "netmask": line.netmask if line.netmask else "",
             "gateway": line.gateway if line.gateway else "",
             "dns": line.ip_dns.dns if line.dns else "",
             "available_ip": line.available_ip if line.available_ip else "",
             "supplier_id": line.parent.group.ip_supplier.first().supplier.id if line.parent and line.parent.group.ip_supplier.first() else {},
             "supplier": line.parent.group.ip_supplier.first().supplier.name + ' / ' + line.parent.group.ip_supplier.first().line_code if line.parent and line.parent.group.ip_supplier.first() else ""}
            for line in lines]


def make_table_supplier_ip(lines=None):
    return [{"DT_RowId": "row_" + str(ip_.id),
             "ip": ip_.IP if ip_.IP else "",
             "netmask": ip_.netmask if ip_.netmask else "",
             "gateway": ip_.gateway if ip_.gateway else "",
             "dns": ip_.ip_dns.dns if ip_.ip_dns else "",
             "available_ip": ip_.available_ip if ip_.available_ip else "",
             "isp": ip_.isp if ip_.isp else ""} for ip_ in lines]


def make_table_mpls(lines=None):
    print("makeing table for mpls")
    if lines is None:
        lines = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                          LineDataBank.line_status.__ne__(100),
                                          LineDataBank.product_model.__eq__('MPLS')).order_by(
            LineDataBank.create_time.desc()).all()
    result = [{"DT_RowId": "row_" + str(l.id),
               "customer_name": l.customer_linedata.name,
               "line_code": l.line_code,
               "sub_line_code": l.sub_line_code if l.sub_line_code else "",
               "a_client_addr": l.a_client_addr if l.a_client_addr else "",
               "a_pop_city": l.a_interface.device_interface.machine_room.cities.city if l.a_interface else {},
               "a_pop_city_id": l.a_interface.device_interface.machine_room.cities.id if l.a_interface else {},
               "a_pop": l.a_interface.device_interface.machine_room.name if l.a_interface else "",
               "a_pop_id": l.a_interface.device_interface.machine_room.id if l.a_interface else {},
               "a_pop_device": l.a_interface.device_interface.device_name if l.a_interface else "",
               "a_pop_device_id": l.a_interface.device_interface.id if l.a_interface else {},
               "a_pop_interface": l.a_interface.interface_name if l.a_interface else "",
               "a_pop_interface_id": l.a_interface.id if l.a_interface else {},
               "a_pop_ip": l.a_interface.device_interface.ip if l.a_interface else "",
               "z_client_addr": l.z_client_addr if l.z_client_addr else "",
               "channel": channel_type[l.channel_type] + ":" + str(l.channel_number) + l.channel_unit,
               "vlan": l.vlans.name if l.vlan else '',
               "vlan_desc": l.vlans.desc if l.vlan and l.vlans.desc is not None else "",
               "vlan_type": l.vlans.type if l.vlans else 'access',
               "access_way": l.mpls_attribute.first().access_way if l.mpls_attribute.first() else "",
               "route_protocol": l.mpls_attribute.first().route_protocol if l.mpls_attribute.first() else "",
               "as_number": l.mpls_attribute.first().as_number if l.mpls_attribute.first() else "",
               "vrf": l.mpls_attribute.first().vrf if l.mpls_attribute.first() else "",
               "rt": l.mpls_attribute.first().rt if l.mpls_attribute.first() else "",
               "interconnect_client": l.mpls_attribute.first().mpls_interconnect_ip.ip_list.first().IP if l.mpls_attribute.first() and l.mpls_attribute.first().mpls_interconnect_ip else "",
               "interconnect_pe": l.mpls_attribute.first().mpls_interconnect_ip.ip_list.first().gateway if l.mpls_attribute.first() and l.mpls_attribute.first().mpls_interconnect_ip else "",
               "interconnect_netmask": l.mpls_attribute.first().mpls_interconnect_ip.ip_list.first().netmask if l.mpls_attribute.first() and l.mpls_attribute.first().mpls_interconnect_ip else "",
               "operator": l.operator.username if l.operator else "",
               "biz_contact_name": l.biz_contact.name if l.biz else "",
               "biz_contact_phoneNumber": l.biz_contact.phoneNumber if l.biz else "",
               "biz_contact_email": l.biz_contact.email if l.biz else "",
               "noc_contact_name": l.noc_contact.name if l.noc else "",
               "noc_contact_phoneNumber": l.noc_contact.phoneNumber if l.noc else "",
               "noc_contact_email": l.noc_contact.email if l.noc else "",
               "customer_manager_name": l.customer_manager_contact.name if l.customer_manager else "",
               "customer_manager_phoneNumber": l.customer_manager_contact.phoneNumber if l.customer_manager else "",
               "start_date": str(l.operate_time),
               "stop_date": str(l.line_stop_time) if l.line_stop_time else "",
               "product_type": l.product_type,
               "product_model": l.product_model,
               "line_desc": l.line_desc if l.line_desc else "",
               "validate_rrpp_status": l.validate_rrpp_status,
               "route_protocal": l.mpls_attribute.first().access_way if l.mpls_attribute.first() else "",
               } for l in lines]
    print(result)
    return result


def make_table_mpls_attribute(lines=None):
    r = [{"DT_RowId": "row_" + str(im.id),
          "route_ip": im.IP,
          "route_netmask": im.netmask} for im in lines]
    print(r)
    return r


def make_options():
    mode_dict = {1: "网关模式", 2: "路由模式"}
    return {"a_pop_id": [{}] + [{"label": pop.name, "value": pop.id} for pop in MachineRoom.query.all()],
            "a_pop_city_id": [{}] + [{"label": city.city, "value": city.id} for city in City.query.all()],
            "a_pop_device_id": [{}] + [{"label": device.device_name, "value": device.id} for device in
                                       Device.query.all()],
            "a_pop_interface_id": [{}] + [{"label": interface.interface_name, "value": interface.id} for interface
                                          in Interfaces.query.all()],
            "z_pop_id": [{}] + [{"label": pop.name, "value": pop.id} for pop in MachineRoom.query.all()],
            "z_pop_city_id": [{}] + [{"label": city.city, "value": city.id} for city in City.query.all()],
            "z_pop_device_id": [{}] + [{"label": device.device_name, "value": device.id} for device in
                                       Device.query.all()],
            "z_pop_interface_id": [{}] + [{"label": interface.interface_name, "value": interface.id} for interface
                                          in Interfaces.query.all()],
            "platform_id": [{}] + [{"label": p.name, "value": p.id} for p in Platforms.query.all()],
            "domains": [{}] + all_domains + multi_domains + erps_instance,
            "mode": [{"label": "网关模式", "value": 1}, {"label": "路由模式", "value": 2}],
            "supplier_id": [
                {"label": supplier.supplier.name + " / " + supplier.line_code + " / " + mode_dict[supplier.mode],
                 "value": supplier.id}
                for supplier in IPSupplier.query.filter_by(status=1).all()]
            }
