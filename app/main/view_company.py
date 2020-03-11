from flask import session, render_template, request, jsonify
from flask_login import login_required
from ..models import Permission, User, Role, Area, JobDescription, Customer, MailTemplet, customer_mailtemplet
from ..decorators import permission_required
from .. import logger, db
from .forms import UserModal
from . import main
from ..my_func import get_machine_room_by_area
from sqlalchemy.sql import func
from sqlalchemy import or_


@main.route('/new_customer', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def new_customer():
    data = request.json
    customer_name = data.get('customer_name')
    mail_templet = data.get('mail_templet')
    mt = MailTemplet.query.get(mail_templet) if mail_templet else 1

    logger.info(f'This new company {customer_name} with mail templet id {mt}')

    try:
        if not Customer.query.filter_by(name=customer_name).first():
            new_c = Customer(name=customer_name)
        else:
            new_c = Customer.query.filter_by(name=customer_name).first()
            new_c.status = 1
            new_c.mail_templet = []
        new_c.mail_templet.append(mt)
        db.session.add(new_c)
        db.session.commit()
        logger.info(f'New company {customer_name} add success')
        return jsonify({'status': 'ok', 'content': "新客户添加成功"})
    except Exception as e:
        logger.error(f'new company {customer_name} fail for {e}')
        db.session.rollback()
        return jsonify({'status': 'fail', 'content': "新增客户失败"})


@main.route('/company', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def company():
    if request.method == 'GET':
        logger.info('User {} is checking company list'.format(session['LOGINNAME']))
        mt = [(m.id, m.name) for m in MailTemplet.query.filter_by(status=1).all()]
        return render_template('company.html', mail_templet=mt)

    elif request.method == 'POST':
        logger.debug(request.form)
        search_content = request.form.get(
            'query[search_content]') if 'query[search_content]' in request.form.keys() else ''

        page_start = (int(request.form.get('datatable[pagination][page]', '0')) - 1) * 10
        length = int(request.form.get('datatable[pagination][perpage]'))

        base_sql = Customer.query. \
            outerjoin(customer_mailtemplet). \
            outerjoin(MailTemplet).filter(Customer.status.__eq__(1),
                                          func.concat(func.ifnull(Customer.name, ''),
                                                      func.ifnull(MailTemplet.name, '')).contains(search_content))

        data = [{'id': c.id,
                 'customer_name': c.name if c.name else "",
                 'mail_templet': c.mail_templet[0].name if c.mail_templet else '',
                 'biz_contact': ', '.join(
                     [x.name for x in c.contacts.filter_by(type='biz_contact').all()]) if c.contacts else "",
                 'noc_contact': ', '.join(
                     [x.name for x in c.contacts.filter_by(type='noc_contact').all()]) if c.contacts else "",
                 'customer_manager': ', '.join(
                     [x.name for x in c.contacts.filter_by(type='customer_manager').all()]) if c.contacts else "",
                 }
                for c in
                base_sql.order_by(Customer.create_date.desc()).offset(page_start).limit(length)]

        recordsTotal = base_sql.count()

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


@main.route('/customer_update', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def customer_update():
    data = request.json
    update_customer_name = data.get('update_customer_name')
    mail_templet_update = data.get('mail_templet_update')

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


@main.route('/customer_delete', methods=['POST'])
@login_required
@permission_required(Permission.MAN_ON_DUTY)
def customer_delete():
    data = request.json
    customer_id = data.get('customer_id')
    customer = Customer.query.get(customer_id)
    logger.debug('User {} is deleting customer {}'.format(session['LOGINNAME'], customer.name))

    if Role.query.filter_by(id=session['ROLE']).first().permissions < Role.query.filter_by(
            name='SNOC').first().permissions:
        logger.debug(session['ROLE'])
        return jsonify({'status': 'fail', 'content': '无权操作'})
    else:
        logger.info(f'try to delete {customer.id}:{customer.name}')
        try:
            # 9 means deleted
            customer.status = 9
            db.session.add(customer)
            db.session.commit()
            logger.info(f'{customer.name} is deleted')
            return jsonify({'status': 'OK', 'content': '客户删除成功'})
        except Exception as e:
            logger.error('Delete user fail:{}'.format(e))
            return jsonify({'status': 'fail', 'content': '客户删除失败'})
