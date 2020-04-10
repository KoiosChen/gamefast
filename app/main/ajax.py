from flask import request, jsonify, session
from flask_login import login_required
from ..models import Device, MachineRoom, Interfaces, City, Permission, all_domains, multi_domains, erps_instance, \
    LineDataBank, CutoverOrder, channel_type, MailTemplet, company_regex, MPLS, IPSupplier, Files, Post, Customer, \
    Platforms
from ..proccessing_data.datatable_action import oss_operator, edit, remove, create_supplier, edit_supplier, \
    create_supplier_ip, create_dia_ip, remove_dia_ip, edit_dia_ip, edit_mpls_route, remove_mpls_route, \
    create_mpls_route, remove_supplier_ip, create_machine_room, edit_machine_room, remove_machine_room, create_device, \
    edit_device, remove_device
from ..decorators import permission_required
from .. import logger, db, nesteddict, redis_db
from . import main
from collections import defaultdict
from ..proccessing_data.get_datatable import make_table, make_options, make_table_vxlan, make_table_dia, make_table_ip, \
    make_table_mpls, make_table_mpls_attribute, make_table_ip_supplier, make_table_supplier_ip, make_table_machine_room, \
    make_table_device, make_table_interface
import json
import requests
import datetime
import re
from mailmerge import MailMerge
from ..MyModule.SendMail import sendmail
from ..MyModule.process_datetime import format_daterange
from ..MyModule.prepare_sql import search_sql
from ..MyModule import SyncDevice
import os
from sqlalchemy import or_
from ..common import success_return, false_return
import time


@main.route('/file_list', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def file_list():
    """
    只能上传线路资料表中记录的文件
    """
    if request.method == 'POST':
        row_id = request.form.get('query[row_id]', '')
        print(row_id)
        session['file_uploading_line_id'] = row_id.split('_')[1]
        page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
        length = int(request.form.get('datatable[pagination][perpage]'))

        data = [{'id': file.id,
                 'name': file.name,
                 'file_path': file.file_path
                 }
                for file in
                Files.query.filter_by(line_order=row_id.split('_')[1]).order_by(Files.create_time).offset(
                    page_start).limit(length)]

        recordsTotal = MachineRoom.query.count()

        rest = {
            "meta": {
                "page": int(request.form.get('datatable[pagination][page]')),
                "pages": int(recordsTotal) / int(length),
                "perpage": int(length),
                "total": int(recordsTotal),
                "sort": "asc",
                "field": "ShipDate"
            },
            "data": data
        }
        return jsonify(rest)


@main.route('/cutover_order', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def cutover_order():
    if request.method == 'POST':
        page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
        length = int(request.form.get('datatable[pagination][perpage]'))

        data = [{'id': cutover.id,
                 'total': cutover.total,
                 'cutover_starttime': cutover.cutover_starttime,
                 'cutover_stoptime': cutover.cutover_stoptime,
                 'cutover_send_date': cutover.cutover_send_date,
                 'cutover_atoz': cutover.cutover_from_to,
                 'templet': cutover.mailtemplet.name,
                 'create_time': cutover.create_time
                 }
                for cutover in
                CutoverOrder.query.order_by(CutoverOrder.create_time.desc()).offset(page_start).limit(length)]

        recordsTotal = CutoverOrder.query.count()

        rest = {
            "meta": {
                "page": int(request.form.get('datatable[pagination][page]')),
                "pages": int(recordsTotal) / int(length),
                "perpage": int(length),
                "total": int(recordsTotal),
                "sort": "asc",
                "field": "ShipDate"
            },
            "data": data
        }
        return jsonify(rest)


@main.route('/send_cutover_mail', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def send_cutover_mail():
    new_cutorder = CutoverOrder()
    filepath = os.path.join('mail_result', new_cutorder.id)
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    else:
        raise FileExistsError(f'{filepath} exist!')
    # 初始化部分变量
    company_mailtemplet = nesteddict()
    atoz = nesteddict()
    cutover_atoz = list()

    # 获取页面传递的参数
    logger.debug(request.get_json())
    mail_json = request.get_json()
    cutover_datetime = mail_json.get('cutover_datetime', None)
    cutover_send_date = mail_json.get('cutover_send_date', None)
    cutover_pops = mail_json.get('pops')
    cutover_title = mail_json.get('cutover_title')
    cutover_reason = mail_json.get('cutover_reason')
    cutover_emergency = mail_json.get('cutover_emergency', None)
    cutover_duration = mail_json.get('cutover_duration', '割接')

    # 验证参数
    pass

    # 整理割接范围，
    for a_z in cutover_pops:
        for key, value in a_z.items():
            row, side = re.findall(r'\[(\d+)\]\[(\w+)\]', key)[0]
            # row 第几行 例如第0行   side A或者Z value 城市名称
            atoz[row][side] = value

    for pop in atoz.values():
        cutover_atoz.append('---'.join([pop['A'], pop['Z']]) if pop['A'] != pop['Z'] else pop['A'])
    # 当有多个割接范围的时候，用都好分隔
    cutover_from_to = '，'.join(cutover_atoz)

    # 整理传入的时间范围
    start_time, stop_time = format_daterange(cutover_datetime)

    # 整理邮件落款日期
    send_date = datetime.datetime.strptime(cutover_send_date.strip(),
                                           '%m/%d/%Y') if cutover_send_date else datetime.date.today()

    # 处理相关业务，将线路对象及线路割接内容关联到公司名称下，line_contents在后续处理中需要用set来去重
    for id_ in mail_json.get('ids'):
        __line = LineDataBank.query.get(id_)
        # 导入该客户的邮件模板
        company_mailtemplet[__line.customer_linedata.name]['templet'] = __line.customer_linedata.mail_templet
        # 导入线路资料表对象
        if 'lines' not in company_mailtemplet[__line.customer_linedata.name].keys():
            company_mailtemplet[__line.customer_linedata.name]['lines'] = list()

        company_mailtemplet[__line.customer_linedata.name]['lines'].append(__line)

        # # combine the e-table
        # line_e = '-'.join([__line.a_e if __line.a_e else "",
        #                    __line.main_e if __line.main_e else "",
        #                    __line.z_e if __line.z_e else ""])
        # logger.debug(line_e)

        # # create a list obj to store cutover contents for every line
        # line_contents = list()
        # # literal the items of atoz to check if the cutover content in the line's e-table
        # for _, pop in atoz.items():
        #     if pop['A'] in line_e and pop['Z'] in line_e:
        #         line_contents.append('--'.join([pop['A'], pop['Z']]))
        # # join it by comma and uniq the list by set()
        # company_mailtemplet[__line.customer_linedata.name]['line_contents'] = '，'.join(list(set(line_contents)))
    logger.debug(company_mailtemplet)

    attachments = list()
    for company, mail_detail in company_mailtemplet.items():
        templet_obj = mail_detail['templet'][0] if mail_detail['templet'] and mail_detail['templet'][
            0] is True else MailTemplet.query.get(1)
        template = templet_obj.attachment_path
        document = MailMerge(template)
        the_lines = mail_detail['lines']
        cutover_lines = []
        protect_desc = '主备路由切换，届时延迟增大' if re.search(company_regex, company) else '业务闪断'

        for the_line in the_lines:
            a_pop = the_line.a_interface.device_interface.machine_room.cities.city if the_line.a_interface else ""
            z_pop = the_line.z_interface.device_interface.machine_room.cities.city if the_line.z_interface else ""
            append_content = '--'.join([a_pop, z_pop])
            cutover_status = protect_desc if the_line.protect else '业务中断'
            body06 = the_line.product_model + '业务'  # 目前没有作用，可删除
            cutover_lines.append({'body03': append_content, 'body04': the_line.line_code, 'body05': cutover_status})
        document.merge(customer=company,
                       date_in_title=send_date.strftime("%Y年%m月%d日"),
                       cutover_title=cutover_title,
                       cutover_starttime=start_time.strftime('%Y-%m-%d %H:%M:%S'),
                       cutover_stoptime=stop_time.strftime('%Y-%m-%d %H:%M:%S'),
                       cutover_atoz=cutover_from_to,
                       body01="紧急" if cutover_emergency else '',
                       body02=send_date.strftime("%Y年%m月%d日"),
                       body03=cutover_lines,
                       cutover_duration=cutover_duration,
                       body06=body06)

        filename = company + '_' + new_cutorder.id + '.docx'
        filename = os.path.join(filepath, filename)
        attachments.append(filename)
        document.write(filename)
    try:
        SM = sendmail(subject='割接通知' + str(datetime.datetime.now()), mail_to='597796137@qq.com')
        attrs = list()
        for a in attachments:
            attrs.append(SM.addAttachFile(a))
        # SM.send(addattach=attrs)

        new_cutorder.total = len(attachments)
        new_cutorder.cutover_status = cutover_status
        new_cutorder.cutover_starttime = start_time
        new_cutorder.cutover_stoptime = stop_time
        new_cutorder.cutover_from_to = cutover_from_to
        new_cutorder.cutover_send_date = send_date
        new_cutorder.title_about = cutover_title
        new_cutorder.content = cutover_reason
        new_cutorder.operator = session['SELFID']
        db.session.add(new_cutorder)
        db.session.commit()
        return jsonify({'status': 'true', "content": "邮件发送成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'false', "content": str(e)})


@main.route('/find_lines', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def find_lines():
    logger.debug(request.form)
    param_dict = nesteddict()
    just_chinese = re.compile(r'^[\u4e00-\u9fa5]+$')
    break_flag = False
    page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
    length = int(request.form.get('datatable[pagination][perpage]'))

    for key, value in dict(request.form).items():
        if 'param' in key:
            logger.debug(f'{key} {value}')
            l, k = re.findall(r'\[\d+\]\[\[(\d+)\]\[(\w+)\]\]', key)[0]
            param_dict[l][k] = value
            if k == 'A' or k == 'Z':
                if value and re.search(just_chinese, value):
                    continue
                else:
                    break_flag = True
                    break
    logger.debug(param_dict)

    cutover_dict = dict()
    for key, value in param_dict.items():
        if len(value) == 2:
            cutover_dict[key] = value
    recordsTotal = 0
    if not len(cutover_dict) >= 1:
        logger.debug(f'{param_dict} field not complete jump out')
        data = []
    elif break_flag:
        logger.deb(f"{break_flag}")
        data = []
    else:
        data_line = list()
        lines = LineDataBank.query.all()
        for line in lines:
            line_combine = str(line.a_e) + str(line.main_e) + str(line.z_e)
            for cutover_pop in cutover_dict.values():
                logger.debug(cutover_pop)
                if (cutover_pop['A'] in line_combine) and (cutover_pop['Z'] in line_combine):
                    data_line.append(line)
        data = [{'RecordID': l.id,
                 'customer_name': l.customer_linedata.name,
                 'line_code': l.line_code,
                 'a_to_z': l.a_client_addr + ' - ' + l.z_client_addr,
                 'channel': channel_type[l.channel_type] + ":" + str(l.channel_number) + l.channel_unit,
                 "protect": "否" if l.protect == 0 else "是",
                 'product_model': l.product_model if l.product_model else "",
                 'e-route': str(l.a_e) + '<br>' + str(l.main_e) + '<br>' + str(l.z_e),
                 'start_date': str(l.operate_time) if l.operate_time else ""} for l in data_line]

        recordsTotal = len(data)

    rest = {
        "meta": {
            "page": int(request.form.get('datatable[pagination][page]')),
            "pages": int(recordsTotal) / int(length),
            "perpage": int(length),
            "total": int(recordsTotal),
            "sort": "asc",
            "field": "ShipDate"
        },
        "data": data
    }
    return jsonify(rest)


@main.route('/get_city', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def get_city():
    return jsonify([{'id': c.id, 'city': c.city} for c in City.query.all()])


@main.route('/memo_update', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def memo_update():
    row_id = request.form.get('row_id')
    body = request.form.get('body')
    print('view', body)
    print(row_id)
    line_id = row_id.split('_')[1]

    post = Post(body=body, author_id=str(session['SELFID']), line_id=line_id)
    db.session.add(post)
    db.session.commit()
    return json.dumps({"status": 'OK'}, ensure_ascii=False)


@main.route('/get_memo', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def get_memo():
    params = request.get_data()
    jl = params.decode('utf-8')
    j = json.loads(jl)
    row_id = j['row_id'].split('_')[1]
    posted_body = dict()
    posts = LineDataBank.query.get(row_id).posts.order_by(Post.timestamp.desc()).all()
    i = 0
    for p in posts:
        posted_body[i] = {'username': p.author.username,
                          'phoneNum': p.author.phoneNum,
                          'body': p.body,
                          'body_html': p.body_html,
                          'timestamp': datetime.datetime.strftime(p.timestamp, '%Y-%m-%d %H:%M:%S')}
        i += 1
    print(posted_body)
    return jsonify(json.dumps(posted_body, ensure_ascii=False))


@main.route('/call_api_get_interface', methods=["POST"])
# @login_required
# @permission_required(Permission.MAN_ON_DUTY)
def call_api_get_interface():
    """
    data 中的结构体：
    {"ip": "10.254.1.1"}
    :return:
    """
    logger.debug(request.form)
    target_devices = request.form.get("data", request.json.get("data"))
    logger.debug(f"Login device to get their interface info --> {target_devices}")
    ip_list = list()
    if isinstance(target_devices["ip"], str):
        ip_list.append(target_devices["ip"])
    elif isinstance(target_devices["ip"], list):
        ip_list.extend(target_devices["ip"])
    device_list = list()
    for ip in ip_list:
        device = Device.query.filter_by(ip=ip, status=1).first()
        device_list.append(device)
    return jsonify(SyncDevice.do_sync(device_list, "interface"))


@main.route('/get_route', methods=["POST"])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def get_route():
    session['a_chain_routes'] = []
    session['z_chain_routes'] = []
    session['a_z_routes'] = []
    session['a_chain-e'] = []
    session['z_chain-e'] = []
    session['a_z-e'] = []
    logger.debug('getting main route')
    row_id = request.form.get('data')
    logger.info('get route of id {} in line_data_bank'.format(row_id))
    line_data = LineDataBank.query.get(row_id.split('_')[1])
    if line_data.a_pop_interface and line_data.z_pop_interface and line_data.platform and line_data.domains:
        try:
            api_url = "http://10.250.62.1:5555/route/api"
            headers = {'Content-Type': 'application/json', "encoding": "utf-8"}
            send_content = {"a_city": line_data.a_interface.device_interface.machine_room.cities.city,
                            "z_city": line_data.z_interface.device_interface.machine_room.cities.city,
                            "platform": line_data.line_platform.name,
                            "a_man_platform": line_data.man_line_platform_a.name,
                            "a_man_domains": '_'.join(sorted([d.name for d in line_data.MAN_domains_a])),
                            "z_man_platform": line_data.man_line_platform_z.name,
                            "z_man_domains": '_'.join(sorted([d.name for d in line_data.MAN_domains_z])),
                            "vlan": line_data.vlans.name,
                            "domains": '_'.join(sorted([d.name for d in line_data.domains]))}
            logger.debug(send_content)
            domains = '_'.join(sorted([d.name for d in line_data.domains]))
            r = requests.post(api_url,
                              data=json.dumps(send_content, ensure_ascii=False).encode('utf-8'),
                              headers=headers,
                              timeout=1)
            result = r.json()
            logger.debug(result)
        except Exception as e:
            logger.error(f"{e}")

        try:
            routes = dict()
            a_z_routes = list()
            if 'a_z' in result.keys():
                if isinstance(result['a_z'], dict):
                    if domains in result['a_z'].keys():
                        logger.debug(result)
                        a_z_routes.append(result['a_z'][domains])
                if isinstance(result['a_z'], list):
                    for r in result['a_z']:
                        if isinstance(r, dict):
                            for k, v in r.items():
                                if re.search(r'畸形点', k):
                                    logger.debug(k)
                                    jxd = re.split(r'\s+', k)[2:]
                                    logger.debug(jxd)
                                    for j in jxd:
                                        logger.debug(j)
                                        v = v.replace(j, j + '(畸形点)')
                                        logger.debug(v)
                                a_z_routes.append(v)
                else:
                    a_z_routes.append(result['a_z'][0])

                if a_z_routes:
                    routes['a_z_routes'] = a_z_routes
                    session['a_z_routes'] = a_z_routes

                if 'a_z-e' in result.keys():
                    session['a_z-e'] = result.get('a_z-e')

            if 'a_chain' in result.keys():
                if result.get('a_chain'):
                    routes['a_chain_routes'] = result.get('a_chain')
                    session['a_chain_routes'] = result.get('a_chain')
                if 'a_chain-e' in result.keys():
                    session['a_chain-e'] = result.get('a_chain-e')

            if 'z_chain' in result.keys():
                if result['z_chain']:
                    routes['z_chain_routes'] = result['z_chain']
                    session['z_chain_routes'] = result.get('z_chain')
                if 'z_chain-e' in result.keys():
                    session['z_chain-e'] = result.get('z_chain-e')
            return jsonify({"status": "true", "content": routes})
        except Exception as e:
            logger.error(e)
            return jsonify({"status": "false", "content": "failed to get route for " + str(e)})
    else:
        return jsonify({"status": "false", "content": "缺少计算路由必要字段（'A端信息'，'Z端信息'，'平台'，'环'）"})


@main.route('/get_domain', methods=["POST"])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def get_domain():
    logger.debug('get pop')
    man_domains = {'3': ['domain1', 'domain2'], '4': 'domain2'}
    platform_id = request.form.get('data')
    if not platform_id:
        return jsonify([{}])
    elif platform_id == "1":
        return jsonify(all_domains + multi_domains)
    elif platform_id == "2":
        return jsonify(erps_instance)
    else:
        return jsonify(man_domains[platform_id])


@main.route('/search_city', methods=["POST"])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def search_city():
    logger.debug('search city')
    tag = request.form.get('data')
    if not tag:
        return jsonify({"status": "true", "content": make_options().get("a_pop_city_id")})
    search = "%{}%".format(tag)
    logger.debug(search)
    cities = [{"label": city.city, "value": city.id} for city in City.query.filter(City.city.like(search)).all()]
    logger.debug(cities)
    return jsonify({"status": "true", "content": cities}) if cities and cities[0] else jsonify({"status": "false"})


@main.route('/get_pop', methods=["POST"])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def get_pop():
    logger.debug('get pop')
    city_id = request.form.get('data')
    pops = [{"label": p.name, "value": p.id} for p in MachineRoom.query.filter_by(city=city_id).all()]
    return jsonify(pops)


@main.route('/get_device', methods=["POST"])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def get_device():
    logger.debug('get device')
    machine_room_id = request.form.get('data')
    devices = [{"label": d.device_name, "value": d.id} for d in
               Device.query.filter_by(monitor_status=1, status=1, machine_room_id=machine_room_id).all()]
    return jsonify(devices)


@main.route('/get_interface', methods=["POST"])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def get_interface():
    logger.debug('get interface')
    interfaces = [{"label": i.interface_name, "value": i.id} for i in
                  Interfaces.query.filter_by(device=request.form.get('data'), parent_id=None).all()]
    return jsonify(interfaces)


@main.route('/editor_test', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def editor_test():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}

    elif request.method == 'GET':
        logger.warning(f"line data query {request.args}")
        page_start = int(request.args.get('start'))
        length = int(request.args.get("length"))
        recordsTotal = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                                 LineDataBank.line_status.__ne__(100),
                                                 or_(LineDataBank.product_model.__eq__('DPLC'),
                                                     LineDataBank.product_model.__eq__('DCA'))).count()
        logger.debug(f"{recordsTotal} {int(recordsTotal / length)} {page_start} {length}")
        draw = int(request.args.get('draw'))
        return jsonify({
            "draw": draw,
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsTotal,

            "data": make_table(lines=None, page_start=page_start, length=length),
            "options": make_options(),
            "files": []
        })


@main.route('/line_data_table_postquery', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def line_data_table_postquery():
    s = time.time()
    records_total, search_result = search_sql(request.form, tab=['DPLC', 'DCA'])
    logger.info('To make table')
    data = make_table(lines=search_result)

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": records_total,
        "recordsFiltered": records_total,
        "data": data,
        "options": make_options(data),
        "files": []
    })


@main.route('/vxlan_table_postquery', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def vxlan_table_postquery():
    logger.debug('query_vxlan_table ')
    records_total, search_result = search_sql(request.form, tab=['VXLAN'])
    # logger.debug(search_result)
    data = make_table_vxlan(lines=search_result)

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": records_total,
        "recordsFiltered": records_total,
        "data": data,
        "options": make_options(data),
        "files": []
    })


@main.route('/dia_table_postquery', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def dia_table_postquery():
    logger.debug('query_dia_table ')
    records_total, search_result = search_sql(request.form, tab=['DIA'])
    # logger.debug(search_result)
    data = make_table_dia(lines=search_result)

    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": records_total,
        "recordsFiltered": records_total,
        "data": data,
        "options": make_options(data),
        "files": []
    })


@main.route('/mpls_table_postquery', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def mpls_table_postquery():
    logger.debug('query_mpls_table ')
    records_total, search_result = search_sql(request.form, tab=['MPLS'])
    # logger.debug(search_result)
    data = make_table_mpls(lines=search_result)
    return jsonify({
        "draw": int(request.form.get('draw')),
        "recordsTotal": records_total,
        "recordsFiltered": records_total,
        "data": data,
        "options": make_options(data),
        "files": []
    })


@main.route('/query_vxlan_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_vxlan_table():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}
    elif request.method == 'GET':

        return jsonify({
            "data": make_table_vxlan(),
            "options": make_options(),
            "files": []
        })


@main.route('/query_machine_room_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_machine_room_table():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value + "_machine_room"
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}

    elif request.method == 'GET':
        logger.debug('query_machine_room_table ')
        options_original = make_options()
        options_original['level_id'] = [{"label": "业务站", "value": '1'}, {"label": "光放站", "value": '2'}]
        options_original['status_id'] = [{"label": "在用", "value": '1'}, {"label": "停用", "value": '0'}]
        options_original['type_id'] = [{"label": "自建", "value": '1'},
                                       {"label": "缆信", "value": '2'},
                                       {"label": "第三方", "value": '3'},
                                       {"label": "城网", "value": '4'}]
        options_original['lift_id'] = [{"label": "是", "value": '1'}, {"label": "否", "value": '0'}]
        return jsonify({
            "data": make_table_machine_room(),
            "options": options_original,
            "files": []
        })


@main.route('/query_interface_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_interface_table():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value + "_device"
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}

    elif request.method == 'GET':
        logger.debug('query interface device ')
        device_id = request.args.get("row_id").split("_")[1]
        logger.debug(device_id)
        interfaces = Device.query.get(eval(device_id)).interface.all()
        options_original = make_options()
        return jsonify({
            "data": make_table_interface(interfaces),
            "options": options_original,
            "files": []
        })


@main.route('/query_device_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_device_table():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value + "_device"
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}

    elif request.method == 'GET':
        logger.debug('query_device_table ')
        options_original = make_options()
        options_original['vendor'] = [{},
                                      {"label": "HUAWEI", "value": 'HUAWEI'},
                                      {"label": "CISCO", "value": 'CISCO'},
                                      {"label": "CENTEC", "value": 'CENTEC'}]

        options_original['login_method'] = [{},
                                            {"label": "SSH", "value": 'SSH'},
                                            {"label": "TELNET", "value": 'TELNET'}]
        options_original['device_model'] = [{},
                                            {"label": "CE6850", "value": 'CE6850'},
                                            {"label": "S9303", "value": 'S9303'}]
        options_original['device_belong_id'] = [{"label": owner.name, "value": owner.id} for owner in
                                                Customer.query.filter_by(status=1).all()]
        options_original['machine_room_id'] = [{"label": mr.name, "value": mr.id} for mr in
                                               MachineRoom.query.filter_by(status=1).order_by(MachineRoom.name).all()]
        options_original['platform_id'] = [{"label": p.name, "value": p.id} for p in
                                           Platforms.query.filter_by(status=1).all()]
        return jsonify({
            "data": make_table_device(),
            "options": options_original,
            "files": []
        })


@main.route('/query_ip_supplier_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_ip_supplier_table():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value + "_supplier"
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}

    elif request.method == 'GET':
        logger.debug('query_ipsupplier_table ')
        data = make_table_ip_supplier()
        return jsonify({
            "data": data,
            "options": make_options(data),
            "files": []
        })


@main.route('/edit_supplier_ip', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def edit_supplier_ip():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value + "_supplier_ip"
            elif key == 'site':
                print(key, value)
                processing_data[_id]['site'] = value
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}


@main.route('/edit_dia_ip', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def action_dia_ip():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value + "_dia_ip"
            elif key == 'site':
                print(key, value)
                processing_data[_id]['site'] = value
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}


@main.route('/edit_mpls_route', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def action_mpls_route():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value + "_mpls_route"
            elif key == 'site':
                print(key, value)
                processing_data[_id]['site'] = value
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return jsonify(eval(action)(processing_data)) if action else jsonify({"error": "action not defined"})


@main.route('/query_supplier_ip_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_supplier_ip_table():
    if request.method == 'POST':
        import re
        try:
            row_id = dict(request.form).get('site').split('_')[1]
            print('query ip table ', row_id)
            ip_list = IPSupplier.query.get(row_id).available_ip_group.ip_list.all()
            data = make_table_supplier_ip(ip_list)
            return jsonify({
                "data": data,
                "options": make_options(data),
                "files": []
            })
        except Exception as e:
            logger.error(e)
            return jsonify({
                "data": [],
                "options": make_options([]),
                "files": []
            })

    elif request.method == 'GET':
        logger.debug('query_ip_table ')
        return jsonify({
            "data": [],
            "options": make_options(),
            "files": []
        })


@main.route('/query_dia_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_dia_table():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                print(key, value)
                action = value
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                print(_id, field, value)
                processing_data[_id][field] = value
        return eval(action)(processing_data) if action else {"error": "action not defined"}

    elif request.method == 'GET':
        logger.debug('query_dia_table ')
        data = make_table_dia()
        return jsonify({
            "data": data,
            "options": make_options(data),
            "files": []
        })


@main.route('/query_ip_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_ip_table():
    if request.method == 'POST':
        import re
        try:
            logger.debug(f'query ip table request form is {request.form}')
            row_id = dict(request.form).get('site').split('_')[1]
            print('query ip table ', row_id)
            line = LineDataBank.query.get(row_id)
            ip_list = line.dia_attribute.first().available_dia_ip.ip_list.all()
            data = make_table_ip(ip_list)
            options = make_options(data)
            return jsonify({
                "data": data,
                "options": options,
                "files": []
            })
        except Exception as e:
            return jsonify({
                "data": [],
                "options": make_options([]),
                "files": []
            })

    elif request.method == 'GET':
        logger.debug('query_ip_table ')
        return jsonify({
            "data": [],
            "options": make_options(),
            "files": []
        })


@main.route('/query_mpls_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_mpls_table():
    if request.method == 'POST':
        import re
        editor_data = dict(request.form)
        print(editor_data)
        processing_data = defaultdict(dict)
        action = ''
        for key, value in editor_data.items():
            if key == 'action':
                logger.debug(f"Data from mpls query: {key}, {value}")
                action = value
            else:
                _id, field = re.findall(r"data\[(\w+)\]\[(\w+)\]", key)[0]
                logger.debug(f"{_id}, {field}, {value}")
                processing_data[_id][field] = value
        try:
            return eval(action)(processing_data)
        except Exception as e:
            logger.error(f'{e} action not define')
            return {"error": "action not defined"}

    elif request.method == 'GET':
        logger.debug('query_mpls_table ')
        data = make_table_mpls()
        return jsonify({
            "data": data,
            "options": make_options(data),
            "files": []
        })


@main.route('/query_mpls_attribute_table', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_mpls_attribute_table():
    if request.method == 'POST':
        import re
        try:
            row_id = dict(request.form).get('site').split('_')[1]
            print('query_mpls_attribute_table ', row_id)
            ip_list = MPLS.query.filter_by(line_id=row_id).first().mpls_route_ip.ip_list.all()
            data = make_table_mpls_attribute(ip_list)
            return jsonify({
                "data": data,
                "options": make_options(data),
                "files": []
            })
        except Exception as e:
            return jsonify({
                "data": [],
                "options": make_options([]),
                "files": []
            })

    elif request.method == 'GET':
        logger.debug('query_query_mpls_attribute_table_table ')
        return jsonify({
            "data": [],
            "options": make_options([]),
            "files": []
        })


@main.route('/find_supplier_ip', methods=["POST"])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def find_supplier_ip():
    """
    The data->tag from post is the id of IPSupplier. Firstly use the tag to find the data object, then make a list to reply
    :return:
    """
    import ipaddress
    logger.debug('find_supplier_ip')
    tag = request.form.get('data')
    if not tag:
        return jsonify([])
    search = "%{}%".format(tag)
    logger.debug(search)
    supplier = IPSupplier.query.get(tag)
    ip_network = [{"label": str(ipaddress.ip_network(s.IP + '/' + s.netmask, strict=False)), "value": s.id}
                  for s in supplier.available_ip_group.ip_list.all()]
    logger.debug(ip_network)
    return jsonify({"status": "true", "content": ip_network}) if ip_network and ip_network[0] else jsonify(
        {"status": "false"})
