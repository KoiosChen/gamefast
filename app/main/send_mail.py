from flask import session, render_template, request, jsonify
from flask_login import login_required
from ..models import Permission, Role, Customer, MailTemplet, MailTemplet_Path, MailTemplet_Path_Temp, Cutover_Path_Temp
from ..decorators import permission_required, permission
from .. import logger, db
from . import main
import os
import shutil
from ..MyModule.HashContent import md5_file
from ..proccessing_data.proccess.public_methods import new_linecode
from ..proccessing_data.proccess.public_methods import save_xlsx


@main.route('/update_mail_templet', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
@permission
def update_mail_templet():
    f = request.files.get('file')  # 获取文件对象
    if not os.path.exists(MailTemplet_Path):
        os.mkdir(MailTemplet_Path)
    complete_filename = os.path.join(MailTemplet_Path, f.filename)
    f.save(complete_filename)
    session['mail_templet_upload'] = complete_filename
    f.close()
    return complete_filename


@main.route('/update_cutover_excel', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def update_cutover_excel():
    f = request.files.get('file')  # 获取文件对象
    return save_xlsx(f, Cutover_Path_Temp, 'cutover_source_file')


@main.route('/send_mail', methods=['GET'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def send_mail():
    return render_template('send_mail.html')


@main.route('/new_templet', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def new_templet():
    data = request.json
    hid = data.get('hid', "")
    templet_name = data.get('templet_name')
    templet_desc = data.get('templet_desc')
    templet_filepath = session.get('mail_templet_upload')
    exist_flag = False
    if templet_filepath:
        source_md5 = md5_file(templet_filepath)
    else:
        return jsonify({'status': 'fail', 'content': "未上传文件"})

    # for ef in os.listdir(MailTemplet_Path):
    #     print(ef)
    #     target_file = os.path.join(MailTemplet_Path, ef)
    #     if os.path.isfile(target_file):
    #         target_md5 = md5_file(target_file)
    #         print(target_md5, source_md5)
    #         if target_md5 == source_md5:
    #             logger.info('file exist')
    #             result_filepath = target_file
    #             exist_flag = True
    #             break
    # if exist_flag:
    #     # 如果目标文件夹已经存在该文件，则删除零时文件夹中的文件，直接用目标文件夹中的已存在文件
    #     os.remove(templet_filepath)
    # else:
    #     target_filename = source_md5 + '.' + os.path.split(templet_filepath)[-1].split('.')[-1]
    #     shutil.move(templet_filepath, os.path.join(MailTemplet_Path, target_filename))
    #     result_filepath = os.path.join(MailTemplet_Path, target_filename)

    if not MailTemplet.query.filter_by(name=templet_name).first() and not hid:
        new_one = MailTemplet(name=templet_name, desc=templet_desc, attachment_path=templet_filepath)
    elif hid:
        new_one = MailTemplet.query.get(int(hid))
        if os.path.exists(new_one.attachment_path):
            os.remove(new_one.attachment_path)
        new_one.attachment_path = templet_filepath
        if templet_desc:
            new_one.desc = templet_desc
    else:
        return jsonify({'status': 'fail', 'content': "新增失败，邮件模板名称重复"})

    try:
        db.session.add(new_one)
        db.session.commit()
        session['mail_templet_upload'] = ''
        return jsonify({'status': 'ok', 'content': "新模板添加成功"}) if not hid else jsonify(
            {'status': 'ok', 'content': "模板更新成功"})
    except Exception as e:
        db.session.rollback()
        session['mail_templet_upload'] = ''
        logger.error(f'Add new mail templet fail {e}')
        return jsonify({'status': 'fail', 'content': f"{e}"})


@main.route('/mail_templet_manager', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
@permission
def mail_templet_manager():
    """
    邮件模板管理
    :return:
    """
    if request.method == 'GET':
        logger.info('User {} is checking mail templet list'.format(session['LOGINNAME']))
        mt = [(m.id, m.name) for m in MailTemplet.query.filter_by(status=1).all()]
        return render_template('mail_templet_manager.html')

    elif request.method == 'POST':
        page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
        length = int(request.form.get('datatable[pagination][perpage]'))

        data = [{'id': c.id,
                 'templet_name': c.name,
                 'templet_desc': c.desc,
                 'templet_path': os.path.basename(c.attachment_path),
                 'status': c.status,
                 'bind_company': len(c.customers)
                 }
                for c in
                MailTemplet.query.filter_by(status=1).order_by(MailTemplet.id).offset(page_start).limit(length)]

        recordsTotal = MailTemplet.query.filter_by(status=1).count()

        rest = {
            "meta": {
                "page": int(request.form.get('datatable[pagination][page]')),
                "pages": int(recordsTotal) / int(length),
                "perpage": int(length),
                "total": int(recordsTotal),
                "sort": "asc",
                "field": "ShipDate"
            },
            "data": data
        }
        return jsonify(rest)


@main.route('/update_templet', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def update_templet():
    data = request.json
    templet_name = data.get('templet_name')
    templet_desc = data.get('templet_desc')
    templet_filepath = session.get('mail_templet_upload')
    session['mail_templet_upload'] = ''

    logger.info('User {} is update {}\'s info'.format(session['LOGINNAME'], update_customer_name))
    c = Customer.query.filter_by(name=update_customer_name).first()
    m = MailTemplet.query.get(mail_templet_update)
    c.mail_templet = []
    c.mail_templet.append(m)
    db.session.add(c)
    try:
        db.session.commit()
        return jsonify({"status": "ok", "content": "更新成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "fail", "content": "数据更新失败，可能存在数据冲突"})


@main.route('/disable_templet', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def delete_templet():
    data = request.json
    temlet_id = data.get('temlet_id')
    temlet = MailTemplet.query.get(temlet_id)
    logger.debug('User {} is deleting mail templet {}'.format(session['LOGINNAME'], temlet.name))
    if temlet_id == 1:
        return jsonify({'status': 'fail', 'content': '默认模板不可禁用'})

    if Role.query.filter_by(id=session['ROLE']).first().permissions < Role.query.filter_by(
            name='SNOC').first().permissions:
        logger.debug(session['ROLE'])
        return jsonify({'status': 'fail', 'content': '无权操作'})
    else:
        logger.info(f'try to delete {temlet.id}:{temlet.name}')
        try:
            # 9 means deleted
            temlet.status = False
            db.session.add(temlet)
            db.session.commit()
            logger.info(f'{temlet.name} is deleted')
            return jsonify({'status': 'OK', 'content': '模板禁用成功'})
        except Exception as e:
            logger.error('Delete templet fail:{}'.format(e))
            return jsonify({'status': 'fail', 'content': '模板禁用失败'})


@main.route('/enable_templet', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def enable_templet():
    data = request.json
    temlet_id = data.get('temlet_id')
    temlet = MailTemplet.query.get(temlet_id)
    logger.debug('User {} is deleting mail templet {}'.format(session['LOGINNAME'], temlet.name))

    if Role.query.filter_by(id=session['ROLE']).first().permissions < Role.query.filter_by(
            name='SNOC').first().permissions:
        logger.debug(session['ROLE'])
        return jsonify({'status': 'fail', 'content': '无权操作'})
    else:
        logger.info(f'try to delete {temlet.id}:{temlet.name}')
        try:
            temlet.status = True
            db.session.add(temlet)
            db.session.commit()
            logger.info(f'{temlet.name} is enabled')
            return jsonify({'status': 'OK', 'content': '模板启用成功'})
        except Exception as e:
            logger.error('enable templet fail:{}'.format(e))
            return jsonify({'status': 'fail', 'content': '模板启用失败'})