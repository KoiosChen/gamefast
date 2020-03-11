from flask import request, jsonify
from . import main
from ..models import AlarmRecord, PonAlarmRecord, Permission, LineDataBank, PermissionIP, Interfaces, Device
from .. import logger, db, work_q, nesteddict, redis_db
from ..proccessing_data import datatable_action
from ..proccessing_data.proccess.public_methods import new_data_obj
import re
from flask_login import current_user
from collections import defaultdict
from ..decorators import permission_ip


@main.route('/sync/interface', methods=["POST"])
@permission_ip(PermissionIP)
def sync_interface():
    data = request.json
    # if not line:
    #     return datatable_action.create(**data)
    # else:
    #     return datatable_action.update(**data)
    logger.debug(f'Receive data from device synchronize {data}')
    lock = 'sync_interface_' + data.get('order_number')
    if redis_db.exists(lock):
        redis_db.delete(lock)
        result = data.get('data')
        line = Device.query.filter_by(ip=data.get('order_number')).first()
        if not line:
            return jsonify(
                {'status': 'false', 'content': f"The order number {data.get('order_number')} does not exist!"})

        logger.debug(f'The length of sync interface callback result is {len(result)}')
        if len(result) > 0 and result.get('state') == 1:
            # do something to update the interface data for this device
            try:
                line.device_name = result.get("swname")
                for interface, int_info in result.get("interface").items():
                    update_interface = new_data_obj("Interface", **{"interface_name": interface, "device": line.id})
                    update_interface.interface_desc = int_info.get("DESC")
                    update_interface.interface_type = int_info.get("PORT")
                    update_interface.interface_status = True if int_info.get("PHY") == "up" else False
                    if int_info.get("ETH"):
                        for eth_int in int_info.get("ETH"):
                            new_eth_int = new_data_obj("Interface", **{"interface_name": eth_int,
                                                                       "device": line.id})
                            new_eth_int.parent = update_interface
                            db.session.add(new_eth_int)
                    db.session.add(update_interface)

                db.session.add(line)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        else:
            logger.warning(f"{result} no info for the interface")
        # 这里要根据具体结果修改一下
        return jsonify({'status': 'true'})
    else:
        return jsonify({'status': 'false', 'content': 'The device is not locked'})


@main.route('/verify/ring', methods=["POST"])
@permission_ip(PermissionIP)
def verify_ring():
    data = request.json
    logger.debug(f'Receive data from verify ring {data}')
    if redis_db.exists('check_rrpp_lock') and redis_db.get('check_rrpp_lock') == data.get('order_number'):
        redis_db.delete('check_rrpp_lock')
        result = data.get('data')
        state = 0
        line = LineDataBank.query.filter_by(line_code=data.get('order_number')).first()
        logger.debug(f'length of the result is {len(result)}')
        if len(result) > 0:
            for r in result:
                state += r.get('state')
            logger.debug(f'now the state value is {state}')
            if state == len(result):
                line.validate_rrpp_status = 1
            else:
                line.validate_rrpp_status = 0

            try:
                db.session.add(line)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
        else:
            pass
        # 这里要根据具体结果修改一下

    return jsonify({'status': 'ok'})


@main.route('/oss', methods=["POST"])
@permission_ip(PermissionIP)
def oss():
    data = request.json
    data['original'] = 'oss'
    data['function'] = 'datatable_action'
    logger.debug(f'Receive data from oss {data}')
    work_q.put(data)
    return jsonify({'status': 'ok'})


@main.route('/delete_alarm_record', methods=['POST'])
@permission_ip(PermissionIP)
def delete_alarm_record():
    """
    用于删除告警记录。alarm_record表不删除，只是将alarm_type修改为999；如果是alarm_type 为4， 那么要删除pon_alarm_record中的记录
    POST的是
    :return:
    """
    try:
        if not current_user.can(Permission.NETWORK_MANAGER):
            logger.warn('This user\'s action is not permitted!')
            return jsonify({'status': 'Fail', 'content': '此账号没有权限删除告警记录'})
        print('delete')
        alarm_id = request.json
        print(alarm_id)

        id = alarm_id['alarm_id']

        print(id)

        print('start check')

        alarm_record = AlarmRecord.query.filter_by(id=id).first()

        print(alarm_record)
        print(alarm_record.alarm_type)

        if alarm_record.alarm_type == 4 or alarm_record.alarm_type == 3:
            print(alarm_record.content)
            try:
                ontid = [int(i) for i in eval(re.findall(r'(\{*.+\})', alarm_record.content)[0])]
            except Exception as e:
                ontid = ['PON']
            ip = re.findall(r'(\d+\.\d+\.\d+\.\d+)', alarm_record.content)[0]
            f, s, p = re.findall(r'(\d+/\d+/\d+)', alarm_record.content)[0].split('/')
            print(f, s, p, ontid, ip)
            for ont in ontid:
                pon_alarm_record = PonAlarmRecord.query.filter_by(ip=ip, frame=f, slot=s, port=p, ontid=ont).first()
                if not pon_alarm_record:
                    continue
                db.session.delete(pon_alarm_record)
                db.session.commit()

        alarm_record.alarm_type = 999
        db.session.add(alarm_record)
        db.session.commit()

        return jsonify({'status': 'OK', 'content': '记录已删除'})

    except Exception as e:
        print(e)
        return jsonify({'status': 'Fail', 'content': str(e)})


@main.route('/assets/<uuid:name>', methods=["GET", "POST"])
def assets(name):
    logger.debug(f">>> Get uuid name: {name}")
    return jsonify({'status': 'ok', "content": name})
