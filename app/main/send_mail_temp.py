from flask import request, jsonify, session, render_template
from flask_login import login_required
from ..models import Permission, LineDataBank, CutoverOrder, MailTemplet, company_regex, MailResult_Path
from ..decorators import permission_required
from .. import logger, db, nesteddict
from . import main
import datetime
import re
from mailmerge import MailMerge
from ..MyModule.SendMail import sendmail
from ..MyModule.ImportData import import_cutover_file
from ..proccessing_data.proccess.public_methods import new_data_obj
import os


@main.route('/send_cutover_mail_from_excel', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def send_cutover_mail_from_excel():
    if not session['cutover_source_file']:
        return jsonify({'status': 'false', 'content': '未上传文件'})

    new_cutorder = CutoverOrder()

    logger.debug(new_cutorder)
    logger.debug(MailResult_Path)
    filepath = os.path.join(MailResult_Path, new_cutorder.id)
    if not os.path.exists(filepath):
        logger.debug(f'create new result director {filepath}')
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
    cutover_duration = mail_json.get('cutover_duration') if mail_json.get('cutover_duration') else "割接"
    cutover_email = mail_json.get('cutover_email')

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
    if cutover_datetime:
        start_time, stop_time = cutover_datetime.split(' - ')
        start_time = datetime.datetime.strptime(start_time.strip(), '%Y/%m/%d %H:%M:%S')
        stop_time = datetime.datetime.strptime(stop_time.strip(), '%Y/%m/%d %H:%M:%S')
        logger.debug('cutover start from {} to {}'.format(start_time, stop_time))
    else:
        start_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
        stop_time = datetime.datetime(2100, 12, 31, 23, 59, 59)

    # 整理邮件落款日期
    send_date = datetime.datetime.strptime(cutover_send_date.strip(),
                                           '%m/%d/%Y') if cutover_send_date else datetime.date.today()

    # 处理相关业务，将线路对象及线路割接内容关联到公司名称下，line_contents在后续处理中需要用set来去重
    for id_ in import_cutover_file(session.get('cutover_source_file'), 'Sheet1'):
        # 导入该客户的邮件模板
        if id_.get("customer_name"):
            customer = new_data_obj('Customer', **{'name': id_.get("customer_name")})
            company_mailtemplet[customer.name]['templet'] = customer.mail_templet
            # 导入线路资料表对象
            if 'lines' not in company_mailtemplet[customer.name].keys():
                company_mailtemplet[customer.name]['lines'] = list()

            company_mailtemplet[customer.name]['lines'].append(id_)
        else:
            continue

    logger.debug(f">>>> company and mailtemplet {company_mailtemplet}")

    attachments = list()
    for company, mail_detail in company_mailtemplet.items():
        templet_obj = mail_detail['templet'][0] if mail_detail['templet'] and mail_detail['templet'][
            0] else MailTemplet.query.get(1)
        mail_title = templet_obj.mail_title
        template = templet_obj.attachment_path
        document = MailMerge(template)
        the_lines = mail_detail['lines']
        cutover_lines = []
        protect_desc = '主备路由切换，届时延迟增大' if re.search(company_regex, company) else '主备路由切换'

        merage_fields = document.get_merge_fields()

        logger.debug(merage_fields)

        for the_line in the_lines:
            append_content = the_line.get('line_content')
            cutover_status = protect_desc if the_line.get("protect") == '是' else '业务中断'
            # body06 = the_line.product_model + '业务' # 目前没有作用，可删除
            cutover_lines.append({'body03': str(append_content),
                                  'body04': str(the_line.get("line_code")),
                                  'body05': str(cutover_status)} if 'body05' in merage_fields else
                                 {
                                     'body03': str(append_content),
                                     'body04': str(the_line.get("line_code"))
                                 })
        emergency = "紧急" if cutover_emergency else ''
        document.merge(customer=company,
                       date_in_title=start_time.strftime("%Y年%m月%d日"),
                       cutover_title=cutover_title,
                       cutover_starttime=start_time.strftime('%Y-%m-%d %H:%M'),
                       cutover_stoptime=stop_time.strftime('%Y-%m-%d %H:%M'),
                       cutover_atoz=cutover_from_to,
                       body01=emergency,
                       body02=send_date.strftime("%Y年%m月%d日"),
                       body03=cutover_lines,
                       cutover_reason=cutover_reason,
                       cutover_duration=cutover_duration)

        filename = mail_title + f"{emergency}割接通知" + "-" + str(company) + '.docx'
        filename = os.path.join(filepath, filename)
        attachments.append(filename)
        document.write(filename)
        document.close()
    try:
        SM = sendmail(subject='割接通知自动汇总_' + str(datetime.datetime.now()))
        attrs = list()
        for a in attachments:
            attrs.append(SM.addAttachFile(a))
        send_flag = True
        if send_flag:
            if SM.send(addattach=attrs):
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
                session['cutover_source_file'] = ""
                return jsonify({'status': 'true', "content": "邮件发送成功"})
            else:
                return jsonify({'status': 'false', "content": "邮件发送失败"})
        else:
            return jsonify({'status': 'false', "content": "未配置发送邮件"})
    except Exception as e:
        db.session.rollback()
        session['cutover_source_file'] = ""
        return jsonify({'status': 'false', "content": str(e)})
