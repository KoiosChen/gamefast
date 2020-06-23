from flask import request, jsonify, render_template, session
from flask_login import login_required
from ..models import Permission, API_URL, SMSOrder, SMSSendResult, PermissionIP
from ..decorators import permission_required, permission_ip
from .. import logger, db, nesteddict, redis_db
from . import sms
import re
import uuid
from ..MyModule.RequestPost import post_request
from ..proccessing_data.proccess.public_methods import new_data_obj
import json
from ..common import success_return, false_return
from collections import defaultdict
from ..proccessing_data.get_datatable import make_options, make_send_result


# SMS_TEMPLATE = {"SMS_188990047": {'name': "港华", "content": '尊敬的客户：您好！关于贵司线路编号{order}，节点{node} 发生故障，中断时间：{time}。最新进展：{progress}。烦请知悉！服务热线：400-720-8880', "white_list": "18420020137,18971592928,13387542469,18627858376", "sign": "应通科技"},"SMS_190789590": {'name': "港华割接通知", "content": "尊敬的客户：您好！接机房通知，定于{time}对{place}进行紧急割接，届时影响贵司{order}，具体影响节点已发送邮件到贵司邮箱，请注意查收，由于割接带来的不便，我们深表歉意。", "white_list": "18420020137,18971592928,13387542469,18627858376", "sign": "应通科技"}}


@sms.route('/sms', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def send_mail():
    SMS_TEMPLATE = json.loads(redis_db.get('SMS_TEMPLATE')) if redis_db.exists('SMS_TEMPLATE') else {}
    return render_template('send_sms.html', sms_template=[[key, value['name']] for key, value in SMS_TEMPLATE.items()])


@sms.route('/sms_template_attributes', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def sms_template_attributes():
    SMS_TEMPLATE = json.loads(redis_db.get('SMS_TEMPLATE')) if redis_db.exists('SMS_TEMPLATE') else {}

    args = request.json
    template_id = args['template_id']
    if not template_id:
        return jsonify({"code": "false", "message": "无模板"})
    if template_id not in SMS_TEMPLATE:
        return jsonify({"code": "false", "message": "模板不存在"})
    template = SMS_TEMPLATE[template_id]
    template['params'] = re.findall(r'{(\w+)}', template['content'])
    template['id'] = template_id
    logger.debug(template)
    return jsonify({"code": "success", "data": template, "message": "请求成功"})


@sms.route('/send_sms_via_ali', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def send_sms_via_ali():
    SMS_TEMPLATE = json.loads(redis_db.get('SMS_TEMPLATE')) if redis_db.exists('SMS_TEMPLATE') else {}

    args = request.json
    logger.debug(args)
    phones = args['phones'].replace(' ', '').replace('，', ',')
    args['phones'] = ','.join([x.strip('\u202c').strip('\u202d') for x in phones.split(',')])
    template_id = args.get("template_id")

    if template_id in SMS_TEMPLATE.keys():
        template = SMS_TEMPLATE[template_id]
        args['sign'] = template['sign']
        args['order_number'] = str(uuid.uuid4())
        result = post_request(API_URL.get('ali_sms'), args)
        logger.debug(result)
        content = template['content'].format(**args['params'])
        new_order = new_data_obj('SMSOrder',
                                 **{'id': args['order_number'],
                                    'total': len(args['phones'].split(',')),
                                    'phones': args['phones'],
                                    'sent_content': f"【{template['sign']}】" + content,
                                    'operator': session['SELFID']})
        phone_list = args['phones'].split(',')
        for phone in phone_list:
            new_data_obj('SMSSendResult', **{'phone': phone, 'sms_order': new_order})
        return jsonify({"code": "success", "message": result})
    else:
        return jsonify({"code": "false", "message": "模板不存在"})


@sms.route('/sms_order', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def sms_order():
    if request.method == 'POST':
        page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
        length = int(request.form.get('datatable[pagination][perpage]'))

        data = [{'id': sms.id,
                 'total': sms.total,
                 'success': sms.success,
                 'fail': sms.fail,
                 'phones': sms.phones,
                 'sent_content': sms.sent_content,
                 'operator': sms.sms_sender.username,
                 'sent_time': sms.create_time
                 }
                for sms in
                SMSOrder.query.order_by(SMSOrder.create_time.desc()).offset(page_start).limit(length)]

        recordsTotal = SMSOrder.query.count()

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


@sms.route('/sms_send_result', methods=['POST'])
@permission_ip(PermissionIP)
def sms_send_result():
    data = request.json
    logger.debug(f'>>>> Get callback of sms: {data}')
    order_number = data.get('order_number')
    phone = data.get('phone_number')
    status = data['data']['SendStatus']
    send_date = data['data']['SendDate']
    err_code = data['data']['ErrCode']
    order = SMSOrder.query.get(order_number)
    if order:
        phone_ = order.send_results.filter_by(phone=phone).first()
        logger.debug(f'>>>> send result of {order} is {phone_}')
        if phone_:
            phone_.status = status
            phone_.err_code = err_code
            phone_.send_date = send_date
            db.session.add(phone_)
            db.session.commit()
            return success_return(msg='更新成功')
        else:
            return false_return(msg=f'<{phone}> 订单中不存在此号码')
    else:
        return false_return(msg=f'<{order_number}> 订单号不存在')


@sms.route('/query_send_result_table', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def query_send_result_table():
    logger.debug('query interface device ')
    _id = request.args.get("row_id")
    logger.debug(_id)
    sms_order = SMSOrder.query.get(_id).send_results.all()
    options_original = make_options()
    return jsonify({
        "data": [] if not sms_order else make_send_result(sms_order),
        "options": options_original,
        "files": []
    })
