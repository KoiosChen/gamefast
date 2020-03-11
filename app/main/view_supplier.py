from flask import render_template, request, session
from . import main
from .. import db
from .forms import PostForm
import os
from ..models import UploadFile_Path, Files
from ..models import UploadFile_Path, Files, Permission
from flask_login import login_required
from ..decorators import permission_required


@main.route('/ip_supplier', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def ip_supplier():
    modal_form = PostForm()
    return render_template('ip_supplier.html', modal_form=modal_form)
