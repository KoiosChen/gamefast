from functools import wraps
from flask import abort, request, jsonify
from flask_login import current_user
from .models import Permission
from . import logger


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                logger.warn('This user\'s action is not permitted!')
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print('{}.{}'.format(f.__module__, f.__name__))
        print(f.__doc__)
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


def permission_ip(permission_ip_list):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.info(
                'IP {} is getting insurance proposal'.format(
                    request.headers.get('X-Forwarded-For', request.remote_addr)))
            if request.headers.get('X-Forwarded-For', request.remote_addr) not in permission_ip_list:
                abort(jsonify({'code': 'fail', 'message': 'IP ' + request.remote_addr + ' not permitted', 'data': ''}))
            return f(*args, **kwargs)

        return decorated_function

    return decorator
