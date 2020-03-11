from flask import request, jsonify
from . import main
from ..models import AlarmRecord, SyslogAlarmConfig, Syslog, LineDataBank
from .. import redis_db, logger
import datetime
from sqlalchemy import and_, func
from ..MyModule.Counter import manage_key
from ..MyModule.HashContent import md5_content
from collections import defaultdict
from sqlalchemy import or_, and_


def nesteddict():
    """
    构造一个嵌套的字典
    :return:
    """
    return defaultdict(nesteddict)


@main.route('/work_progress_counter', methods=['POST'])
def work_progress_counter():
    """
    用于计算工单完成数量
    :return:
    """
    import numpy as np

    def _do_count(required_field, lines):
        new_order = 0
        uncompleted_order = 0
        completed_order = 0
        _tmp = 0
        for dl in lines:
            for rf in required_field:
                if 'attribute' in rf:
                    if getattr(dl, rf).all():
                        _tmp += 1
                elif getattr(dl, rf):
                    _tmp += 1
            if _tmp == len(required_field):
                completed_order += 1
            elif _tmp == 0:
                new_order += 1
            else:
                uncompleted_order += 1
            _tmp = 0
        return np.array([new_order, completed_order, uncompleted_order])

    dplc_required_field = {'a_pop_interface', 'z_pop_interface', 'vlan', 'platform', 'main_route'}
    cloud_required_field = {'a_pop_interface', 'z_pop_interface', 'vlan', 'platform', 'main_route', 'cloud_attribute'}
    dplc_lines = LineDataBank.query.filter_by(product_model='DPLC', record_status=1).all()
    cloud_lines = LineDataBank.query.filter(or_(LineDataBank.product_model.__eq__('DCA'),
                                                LineDataBank.product_model.__eq__('SDWAN')),
                                            LineDataBank.record_status.__eq__(1)).all()

    count_result = _do_count(dplc_required_field, dplc_lines) + _do_count(cloud_required_field, cloud_lines)
    print(count_result)
    return jsonify({'status': 'Success',
                    'content': {'new_order': int(count_result[0]),
                                'completed_order': int(count_result[1]),
                                'uncompleted_order': int(count_result[2])}})


@main.route('/validate_line_counter', methods=['POST'])
def validate_line_counter():
    """
    用于统计线路检测结果
    :return:
    """
    pending = LineDataBank.query.filter_by(record_status=1, validate_rrpp_status=2).count()
    success = LineDataBank.query.filter_by(record_status=1, validate_rrpp_status=1).count()
    fail = LineDataBank.query.filter_by(record_status=1, validate_rrpp_status=0).count()

    return jsonify({'status': 'Success', 'content': {"pending": pending, "success": success, "fail": fail}})


@main.route('/product_model_counter', methods=['POST'])
def product_model_counter():
    """
    用于统计线路类型
    :return:
    """

    def __c(a, b):
        return [a, str(int((a / b) * 100)) + '%']

    print('product model counter')
    dplc = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                     LineDataBank.product_model.__eq__("DPLC")).count()
    sdwan_dca = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                          or_(LineDataBank.product_model.__eq__("SDWAN"),
                                              LineDataBank.product_model.__eq__("DCA"))).count()
    hl = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                   LineDataBank.product_model.__eq__("HL")).count()
    ix = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                   LineDataBank.product_model.__eq__("IX")).count()
    dia = LineDataBank.query.filter(LineDataBank.record_status.__eq__(1),
                                    LineDataBank.product_model.__eq__("DIA")).count()
    total = LineDataBank.query.filter_by(record_status=1).count()

    return jsonify({'status': 'Success',
                    'content': {"dplc": __c(dplc, total),
                                "sdwan_dca": __c(sdwan_dca, total),
                                "hl": __c(hl, total),
                                "ix": __c(ix, total),
                                "dia": __c(dia, total)
                                }
                    })


@main.route('/today_syslog_counter', methods=['POST'])
def today_syslog_counter():
    """
    用于统计返回当天syslog数量
    :return:
    """
    try:
        logger.debug('in today_syslog_counter api')
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)

        todaySyslogCounter = Syslog.query.filter(
            and_(Syslog.logtime.__ge__(datetime.datetime(now.year, now.month, now.day, 0, 0, 0, 0)),
                 Syslog.logtime.__le__(
                     datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second,
                                       now.microsecond)))).count()

        yesterdaySyslogCounter = Syslog.query.filter(
            and_(Syslog.logtime.__ge__(
                datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)),
                Syslog.logtime.__le__(
                    datetime.datetime(yesterday.year, yesterday.month, yesterday.day, yesterday.hour,
                                      yesterday.minute, yesterday.second,
                                      yesterday.microsecond)))).count()

        print('today syslog counter:', todaySyslogCounter)
        return jsonify({'status': 'Success', 'content': todaySyslogCounter,
                        'compare': int(todaySyslogCounter) - int(yesterdaySyslogCounter)})

    except Exception as e:
        print(e)
        return jsonify({'status': 'Fail', 'content': 0})


@main.route('/alarm_counter', methods=['POST'])
def alarm_counter():
    """
    用于统计返回当天告警出发数量
    :return:
    """
    try:
        now = datetime.datetime.now()

        todayAlarmCounter = AlarmRecord.query.filter(
            and_(AlarmRecord.create_time.__ge__(datetime.datetime(now.year, now.month, now.day, 0, 0, 0, 0)),
                 AlarmRecord.create_time.__le__(
                     datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second,
                                       now.microsecond)))).count()

        print('today alarm counter', todayAlarmCounter)

        return jsonify({'status': 'Success', 'content': todayAlarmCounter if todayAlarmCounter else 0})

    except Exception as e:
        print(e)
        return jsonify({'status': 'Fail', 'content': 0})


@main.route('/wechat_counter', methods=['POST'])
def wechat_counter():
    """
    用于统计返回当天微信告警发送成功百分比
    :return:
    """
    try:
        wechat_presend = redis_db.get(manage_key(key='wechatPreSend', date_type='today'))

        wechat_sent = redis_db.get(manage_key(key='wechatSent', date_type='today'))

        if wechat_presend and wechat_sent:
            send = int(wechat_presend)
            sent = int(wechat_sent)
            percent_success_send = int((sent / send) * 10000) / 100

            print(send, sent, percent_success_send)

            return jsonify({'status': 'Success',
                            'content': str(percent_success_send) if percent_success_send <= 100 else 100 + '%'})
        else:
            return jsonify({'status': 'Fail', 'content': 0})

    except Exception as e:
        logger.error(e)
        return jsonify({'status': 'Fail', 'content': 0})


@main.route('/realTimeSyslogRate', methods=['POST'])
def realTimeSyslogRate():
    """
    用于统计返回当天告警出发数量
    :return:
    """
    try:
        pre_data_ = int(request.form.get('pre_data', '0'))
        interval_ = int(request.form.get('pre_data'))
        logger.debug('getting real time syslog receiving rate')
        syslog_counter_today = redis_db.get(manage_key(key='syslog_recv_counter', date_type='today'))
        if not syslog_counter_today:
            redis_db.set(manage_key(key='syslog_recv_counter', date_type='today'), '1')
            syslog_counter_today = '1'
        else:
            syslog_counter_today = syslog_counter_today
        print('today\'s syslog counter is:', syslog_counter_today)
        return jsonify({'status': 'Success',
                        'content': (int(syslog_counter_today) - pre_data_) / (
                                interval_ / 1000) if syslog_counter_today and interval_ and pre_data_ != 0 else 0,
                        'pre_data': syslog_counter_today if syslog_counter_today else 0
                        })

    except Exception as e:
        logger.error('get real time syslog receive rate fail for {}'.format(e))
        return jsonify({'status': 'Fail', 'content': 0})


@main.route('/latest_fifth_alarms', methods=['POST'])
def latest_fifth_alarms():
    """
    最新5条告警信息
    :return:
    """
    try:
        now = datetime.datetime.now()

        latest_alarms = AlarmRecord.query.filter(
            and_(AlarmRecord.create_time.__ge__(datetime.datetime(now.year, now.month, now.day, 0, 0, 0, 0)),
                 AlarmRecord.create_time.__le__(
                     datetime.datetime(now.year, now.month, now.day, 23, 59, 59, 59)))).order_by(
            AlarmRecord.create_time.desc()).limit(5)

        fifth = [[info.content, info.create_time] for info in latest_alarms]
        logger.debug('the fifth is {}'.format(fifth))

        if fifth:
            return jsonify({'status': 'Success',
                            'content': fifth
                            })
        else:
            return jsonify({'status': 'Fail',
                            'content': [['当前无记录', datetime.datetime.now()]]
                            })

    except Exception as e:
        logger.error('get real time syslog receive rate fail for {}'.format(e))
        return jsonify({'status': 'Fail', 'content': 0})


@main.route('/keyAlarmRanking', methods=['POST'])
def keyAlarmRanking():
    """
    用于统计返回当天关键字排名列表
    colors = {
        brand:      '#716aca',
        metal:      '#c4c5d6',
        light:      '#ffffff',
        accent:     '#00c5dc',
        primary:    '#5867dd',
        success:    '#34bfa3',
        info:       '#36a3f7',
        warning:    '#ffb822',
        danger:     '#f4516c'
    };
    :return:
    """
    try:
        logger.debug("start to rank the syslog key alarm records")
        colors = ['danger', 'warning', 'info', 'success', 'primary', 'accent', 'light', 'metal', 'brand']
        logger.debug('getting key alarm ranking')

        alarm_keys = SyslogAlarmConfig.query.filter(SyslogAlarmConfig.alarm_type.__ne__('filter')).all()
        all_keys = {manage_key(key=str(k.id) + '_' + md5_content(k.alarm_keyword), date_type='today'): k.alarm_name for
                    k
                    in alarm_keys}

        key_name_counter = []

        for k, v in all_keys.items():
            value = redis_db.get(k)

            if value:
                key_name_counter.append({'name': v,
                                         'value': value})

        if key_name_counter:

            sorted_counter = sorted(key_name_counter, key=lambda k: k['value'])

            counter_len = len(sorted_counter)

            counter_len = counter_len if counter_len <= 9 else 9

            print(sorted_counter[:counter_len])

            return jsonify({'status': 'Success', 'data': sorted_counter[:counter_len],
                            'name': [n['name'] for n in key_name_counter]})

        else:
            return jsonify({'status': 'Fail', 'content': '暂无告警数据'})

    except Exception as e:
        logger.error('get real time syslog receive rate fail for {}'.format(e))
        return jsonify({'status': 'Fail', 'content': 0})


@main.route('/syslog_ranking', methods=['POST'])
def syslog_ranking():
    """
    用于统计返回当天关键字排名列表
    colors = {
        brand:      '#716aca',
        metal:      '#c4c5d6',
        light:      '#ffffff',
        accent:     '#00c5dc',
        primary:    '#5867dd',
        success:    '#34bfa3',
        info:       '#36a3f7',
        warning:    '#ffb822',
        danger:     '#f4516c'
    };
    :return:
    """
    try:
        logger.debug("Starting to rank the syslog records")

        now = datetime.datetime.now()

        today_syslog_ranking = Syslog.query.with_entities(Syslog.device_ip.label('device_ip'),
                                                          func.count('*').label('count')).filter(
            and_(Syslog.logtime.__ge__(datetime.datetime(now.year, now.month, now.day, 0, 0, 0, 0)),
                 Syslog.logtime.__le__(
                     datetime.datetime(now.year, now.month, now.day, 23, 59, 59, 59)))).group_by(
            Syslog.device_ip).order_by(
            func.count('*').label('count').desc()).limit(10)

        target_device = [ranking_device.device_ip for ranking_device in today_syslog_ranking]

        if target_device:
            serverty_dict = {'error': [], 'critical': [], 'alert': [], 'emergency': []}

            legend = ['error', 'critical', 'alert', 'emergency']

            for log in today_syslog_ranking:
                target_devices_logs = Syslog.query.with_entities(Syslog.device_ip.label('device_ip'),
                                                                 Syslog.serverty.label('serverty'),
                                                                 func.count('*').label('count')).filter(
                    and_(Syslog.logtime.__ge__(datetime.datetime(now.year, now.month, now.day, 0, 0, 0, 0)),
                         Syslog.logtime.__le__(
                             datetime.datetime(now.year, now.month, now.day, 23, 59, 59,
                                               59)),
                         Syslog.device_ip.__eq__(log.device_ip))).group_by(Syslog.serverty).all()
                print('the target devices logs have: ', target_devices_logs)
                tmpList = []
                for one_log in target_devices_logs:
                    tmpList.append(one_log.serverty)
                    serverty_dict[one_log.serverty].append(one_log.count)

                for not_matched in list(set(legend) - set(tmpList)):
                    serverty_dict[not_matched].append(0)

            return jsonify({'status': 'Success',
                            'labels': target_device,
                            'error_list': serverty_dict['error'],
                            'critical_list': serverty_dict['critical'],
                            'alert_list': serverty_dict['alert'],
                            'emergency_list': serverty_dict['emergency']})
        else:
            return jsonify(
                {'status': 'Fail', 'labels': ['暂无Syslog记录'], 'error_list': ['0'], 'critical_list': ['0'],
                 'alert_list': ['0'],
                 'emergency_list': ['0']})

    except Exception as e:
        logger.error('get real time syslog receive rate fail for {}'.format(e))
        return jsonify({'status': 'Fail', 'content': 0})
