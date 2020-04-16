from flask import request, jsonify, render_template, session
from flask_login import login_required
from ..models import Permission, API_URL, SMSOrder
from ..decorators import permission_required
from .. import logger, db, nesteddict, redis_db
from . import sms
import re
import uuid
from ..MyModule.RequestPost import post_request
from ..proccessing_data.proccess.public_methods import new_data_obj
import json

# SMS_TEMPLATE = {"1": {'name': "港华", "content": '尊敬的客户：您好！关于贵司线路编号：{order}，节点信息：{node}，带宽：{bandwidth}故障，中断时间：{time}。最近进展：{progress}。烦请知悉！服务热线：400-720-8880',"white_list": "13817730962,15618098089", "sign": "北京应通"}}


SMS_TEMPLATE = json.loads(redis_db.get('SMS_TEMPLATE')) if redis_db.exists('SMS_TEMPLATE') else {}


@sms.route('/sms', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def send_mail():
    return render_template('send_sms.html', sms_template=[[key, value['name']] for key, value in SMS_TEMPLATE.items()])


@sms.route('/sms_template_attributes', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def sms_template_attributes():
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
    args = request.json
    logger.debug(args)
    phones = args['phones']
    phones = phones.replace(' ', '')
    phones = phones.replace('，', ',')
    args['phones'] = phones
    template_id = args.get("template_id")

    if template_id in SMS_TEMPLATE.keys():
        template = SMS_TEMPLATE[template_id]
        args['sign'] = template['sign']
        args['order_number'] = str(uuid.uuid4())
        result = post_request(API_URL.get('ali_sms'), args)
        logger.debug(result)
        content = template['content'].format(**args['params'])
        new_data_obj('SMSOrder',
                     **{'id': args['order_number'],
                        'total': len(args['phones'].split(',')),
                        'phones': args['phones'],
                        'sent_content': f"【{template['sign']}】" + content,
                        'operator': session['SELFID']})
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
