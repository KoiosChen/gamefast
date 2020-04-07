from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors, myapi, walle, log_manager, sys_config, ajax, view_line_data, api_counter, \
    api_pi, send_mail, view_company, view_supplier, send_mail_temp, map
