from flask import request, jsonify
from . import main
from .. import db
from ..models import PiRegister, User, PcapOrder
import json
import time
import requests
from collections import defaultdict


def nesteddict():
    """
    构造一个嵌套的字典
    :return:
    """
    return defaultdict(nesteddict)


@main.route('/submit_pcap_order', methods=["POST"])
def submit_pcap_order():
    data = request.get_json()
    submit_order = PcapOrder(id=data['id'],
                             account_id=data['accountId'],
                             login_name=data['login_name'],
                             username=data['username'],
                             question_description=data['question'],
                             create_time=time.localtime())
    db.session.add(submit_order)
    db.session.commit()
    return jsonify({'status': 'ok', 'content': '工单已提交，请携带对应设备上门'})


@main.route('/pi_register', methods=["POST"])
def pi_register():
    registerInfo = request.json['sysid'].strip()
    print(registerInfo)
    if not registerInfo:
        return jsonify({'status': 'fail', 'content': '未提交正确的信息'})
    else:
        register_record = PiRegister.query.filter_by(sysid=registerInfo.strip()).first()
        print(register_record)
        if not register_record:
            return jsonify({'status': 'fail', 'content': '此设备未绑定'})
        else:
            userinfo = User.query.filter_by(email=register_record.username, status=1).first()
            if not userinfo:
                return jsonify({'status': 'fail', 'content': '绑定用户不存在或者已经失效'})
            else:
                print(userinfo)
                account_dict = nesteddict()
                processing_orders = PcapOrder.query.filter_by(status=1, login_name=register_record.username).all()
                headers = {'Content-Type': 'application/json', "encoding": "utf-8"}
                send_sms_url = 'http://127.0.0.1:54322/get_customer_info'

                for o in processing_orders:
                    send_content = {"account_id": o.account_id, "loginName": "admin", "_hidden_param": True}
                    r = requests.post(send_sms_url, data=json.dumps(send_content, ensure_ascii=False).encode('utf-8'),
                                      headers=headers)
                    result = r.json()
                    if result['status'] == 'OK':
                        account_dict[o.account_id] = \
                            {"password": result['content']['customerListInfo']['customerList'][0]['password'],
                             "question": o.question_description,
                             "order_id": o.id}
                        print(result)

                register_record.times += 1
                register_record.last_register_time = time.localtime()
                db.session.add(register_record)
                db.session.commit()
                return jsonify(
                    {'status': 'ok', 'content': account_dict, 'url': {'r2d2_url': 'http://192.168.2.112:54321',
                                                                      'onu_url': 'http://192.168.2.112:54322',
                                                                      'iperf_server': '192.168.2.112'}})
