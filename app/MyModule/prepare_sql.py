from ..models import Search_LineDataBank, Contacts, Interfaces, Domains, Device, MachineRoom, City, LineDataBank, \
    Customer, Files, Post, User, Vlan, lines_domains, Platforms, VXLAN, DIA, MPLS, IPManager, IPGroup, IPSupplier, \
    man_lines_domains_a, man_lines_domains_z
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from sqlalchemy import or_, and_
from .. import logger
from .process_datetime import format_daterange


def search_sql(post_data, tab):
    """

    :param post_data: it's request.form object from post data
    :param tab: it's a list
    :return: count, search result
    """
    logger.warning(f"line data query {post_data}")

    page_start = int(post_data.get('start'))
    length = int(post_data.get("length"))
    search_field = eval(post_data.get('search_field')) if 'search_field' in post_data.keys() else []
    search_content = post_data.get('search_content') if 'search_content' in post_data.keys() else ""
    search_field_date = post_data.get(
        'search_field_date') if 'search_field_data' in post_data.keys() else 'operate_time'
    search_date_range = post_data.get('search_date_range')

    concat_fields = list()
    or_fields_list = list()

    contact_biz = aliased(Contacts)
    contact_noc = aliased(Contacts)
    contact_customer_manager = aliased(Contacts)
    a_interface = aliased(Interfaces)
    z_interface = aliased(Interfaces)
    a_device = aliased(Device)
    z_device = aliased(Device)
    a_machineroom = aliased(MachineRoom)
    z_machineroom = aliased(MachineRoom)
    a_city = aliased(City)
    z_city = aliased(City)
    # used in dia
    interconnection = aliased(IPManager)
    assigned_ip = aliased(IPManager)
    dia_available_ip = aliased(IPGroup)
    # use in mpls
    mpls_interconnect_group = aliased(IPGroup)
    mpls_route_group = aliased(IPGroup)
    mpls_interconnect_ip = aliased(IPManager)
    mpls_route_ip = aliased(IPManager)
    backbone_platform = aliased(Platforms)
    man_platform_a = aliased(Platforms)
    man_platform_z = aliased(Platforms)
    backbone_domain = aliased(Domains)
    man_domain_a = aliased(Domains)
    man_domain_z = aliased(Domains)

    start_time, stop_time = format_daterange(search_date_range)

    original_search_field = search_field

    if len(search_field) == 0:
        search_field = ["customer_name", "line_code", "product_model", "client_addr", "channel", "vlan",
                        "platform_domain", "pop", "route", "operator", "biz_noc", "customer_manager",
                        "line_desc", "file_name", "memo"]

    base_sql = LineDataBank.query

    if tab == ['VXLAN'] and not len(original_search_field):
        search_field.extend(tab)
    elif tab == ['DIA'] and not len(original_search_field):
        search_field.extend(tab)
    elif tab == ['MPLS'] and not len(original_search_field):
        search_field.extend(tab)

    if search_content:
        for f in search_field:
            if f == 'customer_name':
                base_sql = base_sql.outerjoin(Customer)
                or_fields_list.append(Customer.name.contains(search_content))
            elif f == 'line_code':
                concat_fields.append(func.ifnull(LineDataBank.line_code, ''))
            elif f == 'product_model':
                concat_fields.append(func.ifnull(LineDataBank.product_model, ''))
            elif f == 'client_addr':
                concat_fields.append(func.ifnull(LineDataBank.a_client_addr, ''))
                concat_fields.append(func.ifnull(LineDataBank.z_client_addr, ''))
            elif f == 'channel':
                # channel_type.get(l.channel_type, 9) + ": " + str(l.channel_number) + l.channel_unit,
                concat_fields.append(func.ifnull(LineDataBank.channel_number, 0))
                concat_fields.append(func.ifnull(LineDataBank.channel_unit, ''))
            elif f == 'vlan':
                base_sql = base_sql.outerjoin(Vlan)
                or_fields_list.append(Vlan.name.contains(search_content))
            elif f == 'platform_domain':
                base_sql = base_sql.outerjoin(backbone_platform, LineDataBank.platform == backbone_platform.id). \
                    outerjoin(man_platform_a, LineDataBank.MAN_platform_a == man_platform_a.id). \
                    outerjoin(man_platform_z, LineDataBank.MAN_platform_z == man_platform_z.id). \
                    outerjoin(lines_domains). \
                    outerjoin(backbone_domain). \
                    outerjoin(man_lines_domains_a). \
                    outerjoin(man_domain_a). \
                    outerjoin(man_lines_domains_z). \
                    outerjoin(man_domain_z)

                or_fields_list.append(backbone_platform.name.contains(search_content))
                or_fields_list.append(backbone_domain.name.contains(search_content))
                or_fields_list.append(man_platform_a.name.contains(search_content))
                or_fields_list.append(man_domain_a.name.contains(search_content))
                or_fields_list.append(man_domain_z.name.contains(search_content))
                or_fields_list.append(man_platform_z.name.contains(search_content))
            elif f == 'pop':
                base_sql = base_sql.outerjoin(a_interface, LineDataBank.a_pop_interface == a_interface.id). \
                    outerjoin(z_interface, LineDataBank.z_pop_interface == z_interface.id). \
                    outerjoin(a_device, a_device.id == a_interface.device). \
                    outerjoin(a_machineroom, a_device.machine_room_id == a_machineroom.id). \
                    outerjoin(a_city, a_city.id == a_machineroom.city). \
                    outerjoin(z_device, z_device.id == z_interface.device). \
                    outerjoin(z_machineroom, z_device.machine_room_id == z_machineroom.id). \
                    outerjoin(z_city, z_city.id == z_machineroom.city)
                or_fields_list.append(a_interface.interface_name.contains(search_content))
                or_fields_list.append(a_machineroom.name.contains(search_content))
                or_fields_list.append(a_device.device_name.contains(search_content))
                or_fields_list.append(a_device.ip.contains(search_content))
                or_fields_list.append(a_city.city.contains(search_content))

                or_fields_list.append(z_interface.interface_name.contains(search_content))
                or_fields_list.append(z_machineroom.name.contains(search_content))
                or_fields_list.append(z_device.device_name.contains(search_content))
                or_fields_list.append(z_device.ip.contains(search_content))
                or_fields_list.append(z_city.city.contains(search_content))
            elif f == 'route':
                concat_fields.append(func.ifnull(LineDataBank.main_e, ''))
                concat_fields.append(func.ifnull(LineDataBank.main_route, ''))
                concat_fields.append(func.ifnull(LineDataBank.a_e, ''))
                concat_fields.append(func.ifnull(LineDataBank.z_e, ''))
                concat_fields.append(func.ifnull(LineDataBank.a_chain, ''))
                concat_fields.append(func.ifnull(LineDataBank.z_chain, ''))
            elif f == 'operator':
                base_sql = base_sql.outerjoin(User)
                or_fields_list.append(User.username.contains(search_content))
            elif f == 'biz_noc':
                base_sql = base_sql.outerjoin(contact_biz, LineDataBank.biz == contact_biz.id).outerjoin(contact_noc,
                                                                                                         LineDataBank.noc == contact_noc.id)
                or_fields_list.append(contact_biz.name.contains(search_content))
                or_fields_list.append(contact_biz.email.contains(search_content))
                or_fields_list.append(contact_biz.phoneNumber.contains(search_content))
                or_fields_list.append(contact_noc.name.contains(search_content))
                or_fields_list.append(contact_noc.email.contains(search_content))
                or_fields_list.append(contact_noc.phoneNumber.contains(search_content))
            elif f == 'customer_manager':
                base_sql = base_sql.outerjoin(contact_customer_manager,
                                              LineDataBank.customer_manager == contact_customer_manager.id)
                or_fields_list.append(contact_customer_manager.name.contains(search_content))
                or_fields_list.append(contact_customer_manager.email.contains(search_content))
                or_fields_list.append(contact_customer_manager.phoneNumber.contains(search_content))
            elif f == 'line_desc':
                concat_fields.append(func.ifnull(LineDataBank.line_desc, ''))
            elif f == 'file_name':
                base_sql = base_sql.outerjoin(Files, LineDataBank.id == Files.line_order)
                or_fields_list.append(Files.name.contains(search_content))
            elif f == 'memo':
                base_sql = base_sql.outerjoin(Post, Post.line_id == LineDataBank.id)
                or_fields_list.append(Post.body.contains(search_content))
            elif f == 'VXLAN':
                base_sql = base_sql.outerjoin(VXLAN, VXLAN.line_id == LineDataBank.id)
                or_fields_list.append(VXLAN.bd.contains(search_content))
            elif f == 'DIA':
                base_sql = base_sql. \
                    outerjoin(DIA, DIA.line_id == LineDataBank.id). \
                    outerjoin(interconnection, interconnection.id == DIA.ip). \
                    outerjoin(dia_available_ip, dia_available_ip.id == DIA.available_ip). \
                    outerjoin(assigned_ip, assigned_ip.ip_group == dia_available_ip.id)
                or_fields_list.append(func.concat(func.ifnull(interconnection.IP, ''),
                                                  func.ifnull(interconnection.netmask, ''),
                                                  func.ifnull(interconnection.gateway, ''),
                                                  func.ifnull(interconnection.available_ip, ''),
                                                  func.ifnull(interconnection.desc, '')).contains(search_content))
                or_fields_list.append(func.concat(func.ifnull(assigned_ip.IP, ''),
                                                  func.ifnull(assigned_ip.netmask, ''),
                                                  func.ifnull(assigned_ip.gateway, ''),
                                                  func.ifnull(assigned_ip.available_ip, ''),
                                                  func.ifnull(assigned_ip.desc, '')).contains(search_content))
                or_fields_list.append(DIA.dns.contains(search_content))
            elif f == 'MPLS':
                base_sql = base_sql. \
                    outerjoin(MPLS, MPLS.line_id == LineDataBank.id). \
                    outerjoin(mpls_interconnect_group, MPLS.interconnect_ip == mpls_interconnect_group.id). \
                    outerjoin(mpls_route_group, MPLS.local_route == mpls_route_group.id). \
                    outerjoin(mpls_interconnect_ip, mpls_interconnect_ip.ip_group == mpls_interconnect_group.id). \
                    outerjoin(mpls_route_ip, mpls_route_ip.ip_group == mpls_route_group.id)
                concat_fields.append(func.concat(func.ifnull(MPLS.as_number, ''),
                                                 func.ifnull(MPLS.access_way, ''),
                                                 func.ifnull(MPLS.vrf, ''),
                                                 func.ifnull(MPLS.rt, '')))
                or_fields_list.append(func.concat(func.ifnull(mpls_route_ip.IP, ''),
                                                  func.ifnull(mpls_route_ip.netmask, ''),
                                                  func.ifnull(mpls_route_ip.gateway, ''),
                                                  func.ifnull(mpls_route_ip.available_ip, ''),
                                                  func.ifnull(mpls_route_ip.desc, '')).contains(search_content))
                or_fields_list.append(func.concat(func.ifnull(mpls_interconnect_ip.IP, ''),
                                                  func.ifnull(mpls_interconnect_ip.netmask, ''),
                                                  func.ifnull(mpls_interconnect_ip.gateway, ''),
                                                  func.ifnull(mpls_interconnect_ip.available_ip, ''),
                                                  func.ifnull(mpls_interconnect_ip.desc, '')).contains(search_content))

    fuzzy_sql = or_(func.concat(*concat_fields).contains(search_content),
                    *or_fields_list) if concat_fields else or_(*or_fields_list)

    product_sql = or_(*[LineDataBank.product_model.__eq__(model) for model in tab])

    status_sql = and_(LineDataBank.record_status.__eq__(1), LineDataBank.line_status.__ne__(100))

    logger.debug(search_field_date)

    daterange_sql = and_(getattr(LineDataBank, search_field_date).__le__(stop_time),
                         getattr(LineDataBank, search_field_date).__ge__(start_time))
    if 'search_field_data' in post_data.keys():
        final_sql = base_sql.filter(status_sql, product_sql, fuzzy_sql, daterange_sql)
    else:
        final_sql = base_sql.filter(status_sql, product_sql, fuzzy_sql)

    logger.debug(final_sql)

    records_total = final_sql.group_by(LineDataBank.id).count()

    logger.debug(f">>>> Lines: {records_total} Pages: {int(records_total / length)} from {page_start} to {length}")

    return records_total, final_sql.order_by(LineDataBank.operate_time.desc()).offset(
        page_start).limit(length).all()
