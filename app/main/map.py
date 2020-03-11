from flask import render_template, request, session
from . import main
from .. import db
from .forms import PostForm
import os
from ..models import UploadFile_Path, Files, Permission, Search_LineDataBank, MachineRoom
from flask_login import login_required
from ..decorators import permission_required
from flask import jsonify


@main.route('/baidumap', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def baidumap():
    return render_template('baidumap.html')


@main.route('/locate_machine_room', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def locate_machine_room():
    return jsonify(
        {"status": "OK",
         "content": [{"address": m.address, "city": m.cities.city} for m in MachineRoom.query.all()]})
