import re
from .. import logger


def verify_net_in_net(**kwargs):
    from IPy import IP
    source_net = kwargs.get('source_net')
    target_net = kwargs.get('target_net')
    try:
        if IP(source_net, make_net=True) in IP(target_net, make_net=True):
            return True
        else:
            return {'error': '分配给客户地址不在供应商地址段范围内'}
    except ValueError:
        return {'error': 'IP地址格式错误'}


def verify_network(**kwargs):
    import ipaddress
    ip = kwargs.get('IP')
    netmask = kwargs.get('netmask')
    gateway = kwargs.get('gateway')
    try:
        _ip = ipaddress.ip_address(ip)
        _gateway = ipaddress.ip_address(gateway)
        _network = ipaddress.ip_network(gateway + '/' + netmask, strict=False)
        if _ip in _network:
            print(_network[0], _network[-1])
            if _ip not in (_network[0], _network[-1]) and _gateway not in (_network[0], _network[-1]):
                return True
            else:
                return {'error': '不能用主机位或网络位'}
        else:
            return {'error': 'IP 段不匹配'}
    except ValueError:
        return {'error': 'IP地址格式错误'}


def verify_required(**kwargs):
    r = []
    for key, value in kwargs.items():
        v = verify_fields('required_field', key, value)
        if v is not True:
            r.append(key)
    return {"fieldErrors": [{"name": field, "status": "此字段不能为空"} for field in r]} if r else True


def verify_fields(type_, field, value, vlan_type=None):
    largest_vlan = 10000 if vlan_type == 'vxlan' and field == 'vlan' else 4096

    if type_ == 'vlan':
        if re.search(r'\D+', value) and vlan_type in ('access', 'vxlan'):
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "仅数字"
                    }
                ]
            }
        if not value:
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "This field is required"
                    }
                ]
            }
        value = value.replace('，', ',')
        vlans = re.split(r'\s+|,|，', value)
        if 'to' in vlans:
            i_to = vlans.index('to')
            if not (i_to > 0 and re.search(r'\d+', vlans[i_to - 1]) and re.search(r'\d+', vlans[i_to + 1])):
                return {
                    "fieldErrors": [
                        {
                            "name": field,
                            "status": "vlan范围格式错误"
                        }
                    ]
                }
        for v in vlans:
            if v and v != 'to':
                try:
                    if not isinstance(eval(v), int) or eval(v) < 1 or eval(v) > largest_vlan:
                        return {
                            "fieldErrors": [
                                {
                                    "name": field,
                                    "status": "vlan范围（1-4096）"
                                }
                            ]
                        }
                except Exception as e:
                    logger.error('verify fields error')
                    return {
                        "fieldErrors": [
                            {
                                "name": field,
                                "status": "非法字符"
                            }
                        ]
                    }
        return True
    elif type_ == 'required_field':
        return {
            "fieldErrors": [
                {
                    "name": field,
                    "status": "此字段不能为空！"
                }
            ]
        } if not value else True
    elif type_ == 'name':
        if re.match(r'^[a-zA-Z]+$', value.strip()):
            return True
        elif re.match(r"^[\u4E00-\u9FA5]{2,4}$", value.strip()):
            return True
        else:
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "非法字符"
                    }
                ]
            }
    elif type_ == 'email':
        email_regex = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
        if re.match(email_regex, value.strip()):
            return True
        else:
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "邮箱格式错误"
                    }
                ]
            }
    elif type_ == 'phone':
        if re.match(r'^[1]([3-9])[0-9]{9}$', value.strip()):
            return True
        elif re.match(r'^0\d{2,3}-?\d{7,8}$', value.strip()):
            return True
        else:
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "电话号码格式错误"
                    }
                ]
            }
    elif type_ == 'date':
        import datetime
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
            return True
        except Exception as e:
            logger.error(e)
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "日期(yyyy-mm-dd)格式错误"
                    }
                ]
            }
    elif type_ == 'datetime':
        import datetime
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(e)
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "日期(yyyy-mm-dd HH:MM:SS)格式错误"
                    }
                ]
            }
    elif type_ == 'netmask':
        try:
            if int(value) > 32 or int(value) < 0:
                return {
                    "fieldErrors": [
                        {
                            "name": field,
                            "status": "netmask范围（0~32）"
                        }
                    ]
                }
            else:
                return True
        except ValueError:
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "netmask需为整数（0~32）"
                    }
                ]
            }
    elif type_ == 'IP':
        if not re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", value):
            return {
                "fieldErrors": [
                    {
                        "name": field,
                        "status": "IP地址格式错误"
                    }
                ]
            }
        else:
            return True
    else:
        return {'error': '内部错误'}


def chain_add_validate(x, m):
    return 1 if x in m else 2
