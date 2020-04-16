from flask import Blueprint

sms = Blueprint('sms', __name__)

from . import view_sms