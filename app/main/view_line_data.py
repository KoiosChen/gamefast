from flask import render_template, request, session
from . import main
from .. import db
from .forms import PostForm
import os
from ..models import UploadFile_Path, Files, Permission, Search_LineDataBank
from flask_login import login_required
from ..decorators import permission_required


@main.route('/linedata', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def linedata():
    modal_form = PostForm()
    return render_template('line_data_bank.html', modal_form=modal_form, search_fields=Search_LineDataBank)


@main.route('/upload_fileOfLines', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def upload_file_lines():
    print(UploadFile_Path)
    f = request.files.get('file')  # 获取文件对象
    if not os.path.exists(UploadFile_Path):
        os.mkdir(UploadFile_Path)
    complete_filename = os.path.join(UploadFile_Path, f.filename)
    f.save(complete_filename)
    new_file = Files()
    new_file.name = f.filename
    new_file.file_path = complete_filename
    new_file.line_order = session.get('file_uploading_line_id')
    db.session.add(new_file)
    db.session.commit()
    return complete_filename
