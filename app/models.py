from flask import current_app
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
from . import login_manager
import datetime
import os
import bleach
import uuid
import re


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


lines_domains = db.Table('lines_domains',
                         db.Column('lines', db.Integer, db.ForeignKey('line_data_bank.id'), primary_key=True),
                         db.Column('domains', db.Integer, db.ForeignKey('domains.id'), primary_key=True))

man_lines_domains_a = db.Table('man_lines_domains_a',
                               db.Column('lines', db.Integer, db.ForeignKey('line_data_bank.id'), primary_key=True),
                               db.Column('man_domains', db.Integer, db.ForeignKey('domains.id'), primary_key=True))

man_lines_domains_z = db.Table('man_lines_domains_z',
                               db.Column('lines', db.Integer, db.ForeignKey('line_data_bank.id'), primary_key=True),
                               db.Column('man_domains', db.Integer, db.ForeignKey('domains.id'), primary_key=True))

lines_cutoverorder = db.Table('lines_cutoverorder',
                              db.Column('lines', db.Integer, db.ForeignKey('line_data_bank.id'), primary_key=True),
                              db.Column('cutoverorder', db.String(50), db.ForeignKey('cutover_order.id'),
                                        primary_key=True))

customer_mailtemplet = db.Table('customer_mailtemplet',
                                db.Column('customer', db.Integer, db.ForeignKey('customer.id'), primary_key=True),
                                db.Column('mailtemplet', db.Integer, db.ForeignKey('mail_templet.id'),
                                          primary_key=True))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    REGION_SUPPORT = 0x10
    MAN_ON_DUTY = 0x20
    NETWORK_MANAGER = 0x40
    ADMINISTER = 0x80


class MailTemplet(db.Model):
    __tablename__ = 'mail_templet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    desc = db.Column(db.String(200))
    attachment_path = db.Column(db.String(200), index=True, nullable=False)
    mail_title = db.Column(db.String(100), default='上海游驰')
    mail_content = db.Column(db.String(200))
    mail_signature = db.Column(db.String(200))
    mail_from = db.Column(db.String(50))
    status = db.Column(db.Boolean, default=True)
    cutover_order = db.relationship('CutoverOrder', backref='mailtemplet')


class Files(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    desc = db.Column(db.String(200))
    file_path = db.Column(db.String(200), index=True, nullable=False)
    status = db.Column(db.Boolean, default=True)
    line_order = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class CutoverOrder(db.Model):
    __tablename__ = 'cutover_order'
    id = db.Column(db.String(50), primary_key=True)
    total = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Integer)
    fail = db.Column(db.Integer)
    # 标题中的关键字
    title_about = db.Column(db.String(50))
    # 割接内容
    content = db.Column(db.String(200))
    # 割接状态，例如“造成中断”， “不影响业务”
    cutover_status = db.Column(db.String(100))
    # 割接开始时间
    cutover_starttime = db.Column(db.DateTime)
    # 割接结束时间
    cutover_stoptime = db.Column(db.DateTime)
    # 割接涉及机房
    cutover_from_to = db.Column(db.String(200))
    # 割接涉及的线路编号
    lines = db.relationship('LineDataBank', secondary=lines_cutoverorder, backref=db.backref('cutoverorders'))
    operator = db.Column(db.Integer, db.ForeignKey('users.id'))
    templet = db.Column(db.Integer, db.ForeignKey('mail_templet.id'), default=1)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    cutover_send_date = db.Column(db.Date)

    def __init__(self, **kwargs):
        super(CutoverOrder, self).__init__(**kwargs)
        self.id = str(uuid.uuid1())


class SMSOrder(db.Model):
    __tablename__ = 'sms_order'
    id = db.Column(db.String(64), primary_key=True)
    total = db.Column(db.Integer, default=0)
    success = db.Column(db.Integer)
    fail = db.Column(db.Integer)
    phones = db.Column(db.String(200))
    sent_content = db.Column(db.String(300), comment='已发送内容')
    operator = db.Column(db.Integer, db.ForeignKey('users.id'))
    send_results = db.relationship('SMSSendResult', backref='sms_order', lazy='dynamic')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class SMSSendResult(db.Model):
    __tablename__ = 'sms_send_result'
    id = db.Column(db.String(64), primary_key=True)
    order_id = db.Column(db.String(64), db.ForeignKey('sms_order.id'))
    phone = db.Column(db.String(15))
    status = db.Column(db.SmallInteger, default=1, comment="SendStatus 1：等待回执  2：发送失败。  3：发送成功。")
    send_date = db.Column(db.DateTime)
    err_code = db.Column(db.String(100))
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)

    def __init__(self, **kwargs):
        super(SMSSendResult, self).__init__(**kwargs)
        self.id = str(uuid.uuid1())


class OperateLog(db.Model):
    __tablename__ = 'operate_log'
    id = db.Column(db.Integer, primary_key=True)
    table = db.Column(db.String(20))
    row_id = db.Column(db.Integer)
    old_field = db.Column(db.String(1000))
    new_field = db.Column(db.String(1000))
    operator = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)


class Contacts(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    phoneNumber = db.Column(db.String(50), index=True)
    email = db.Column(db.String(50), index=True)
    address = db.Column(db.String(50), index=True)
    type = db.Column(db.String(20), index=True)
    company = db.Column(db.Integer, db.ForeignKey('customer.id'), index=True)
    lines_biz = db.relationship('LineDataBank', backref='biz_contact', lazy='dynamic',
                                foreign_keys='LineDataBank.biz', )
    lines_noc = db.relationship('LineDataBank', backref='noc_contact', lazy='dynamic',
                                foreign_keys='LineDataBank.noc', )
    line_customer_manager = db.relationship('LineDataBank', backref='customer_manager_contact', lazy='dynamic',
                                            foreign_keys='LineDataBank.customer_manager', )

    supplier_biz = db.relationship('IPSupplier', backref='supplier_biz_contact', lazy='dynamic',
                                   foreign_keys='IPSupplier.biz', )
    supplier_noc = db.relationship('IPSupplier', backref='supplier_noc_contact', lazy='dynamic',
                                   foreign_keys='IPSupplier.noc', )
    supplier_customer_manager = db.relationship('IPSupplier', backref='supplier_customer_manager_contact',
                                                lazy='dynamic',
                                                foreign_keys='IPSupplier.customer_manager', )
    machine_room = db.relationship('MachineRoom', backref='administrator', lazy='dynamic')


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    contacts = db.relationship('Contacts', backref='customers', lazy='dynamic')
    line_data = db.relationship('LineDataBank', backref='customer_linedata', lazy='dynamic')
    interconnection = db.relationship('Interconnection', backref='customer_interconnection', lazy='dynamic')
    # 1 正常 0 无效用户 998 删除
    status = db.Column(db.SmallInteger, default=1)
    create_date = db.Column(db.DateTime, default=datetime.datetime.now)
    devices = db.relationship('Device', backref='device_owner', lazy='dynamic')
    mail_templet = db.relationship('MailTemplet', secondary=customer_mailtemplet, backref=db.backref('customers'))
    ip_supplier = db.relationship('IPSupplier', backref='supplier', lazy='dynamic')

    def __repr__(self):
        return '<Customer name %r>' % self.name


class Interconnection(db.Model):
    __tablename__ = 'interconnection'
    id = db.Column(db.Integer, primary_key=True)
    # ots number ots或者oss中的编号
    order_number = db.Column(db.String(20))
    customer = db.Column(db.Integer, db.ForeignKey('customer.id'), index=True)
    # 引接缆客户端地址
    a_client_addr = db.Column(db.String(200), index=True)
    # 引接缆我司机房
    pop_device = db.Column(db.Integer, db.ForeignKey('device_list.id'), index=True)
    pop_interface = db.Column(db.Integer, db.ForeignKey('interfaces.id'), index=True)
    odf_info = db.Column(db.String(100))
    # 客户设备信息，纯文字记录
    opposite_side_device = db.Column(db.String(100))
    interface_uptime = db.Column(db.DateTime)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Interconnection pop device %r>' % self.pop_device


class Vlan(db.Model):
    __tablename__ = 'vlan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5), index=True, nullable=False)
    # single/qinq/multi_qinq/vxlan/vlan_map
    type = db.Column(db.String(10), index=True, nullable=False, default='single')
    desc = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, db.ForeignKey('vlan.id'))
    parent = db.relationship('Vlan', backref="children", remote_side=[id])
    lines = db.relationship('LineDataBank', backref="vlans", lazy='dynamic')
    ip_supplier = db.relationship('IPSupplier', backref='access_vlan', lazy='dynamic')

    def __repr__(self):
        return '<vlan %r>' % self.name


class Interfaces(db.Model):
    """
    记录设备-> 端口 与ODF 波道的关系，同时记录单端口和eth-trunk的关系
    """
    __tablename__ = 'interfaces'
    id = db.Column(db.Integer, primary_key=True)
    # example: xg1/0/1, eth-trunk0
    interface_name = db.Column(db.String(50), index=True, nullable=False)
    interface_desc = db.Column(db.String(100))
    # switch route eth-trunk vlanif
    interface_type = db.Column(db.String(10))
    # 对接的ODF
    odf = db.Column(db.String(10))
    # 对接的波道
    channel = db.Column(db.String(100))
    interface_status = db.Column(db.Boolean)
    # 预留，用于记录端口配置，或者trunk允许的vlan等
    interface_conf = db.Column(db.String(300))
    device = db.Column(db.Integer, db.ForeignKey('device_list.id'))
    line_a = db.relationship('LineDataBank', backref='a_interface', foreign_keys='LineDataBank.a_pop_interface',
                             lazy='dynamic')
    line_z = db.relationship('LineDataBank', backref='z_interface', foreign_keys='LineDataBank.z_pop_interface',
                             lazy='dynamic')

    domain_owner = db.relationship('Domains', backref='owner_interface', foreign_keys='Domains.owner_block_interface',
                                   lazy='dynamic')
    domain_neighbor = db.relationship('Domains', backref='neighbor_interface',
                                      foreign_keys='Domains.neighbor_block_interface', lazy='dynamic')

    ip_supplier = db.relationship('IPSupplier', backref='supplier_access_interface', lazy='dynamic')
    parent_id = db.Column(db.Integer, db.ForeignKey('interfaces.id'))
    parent = db.relationship('Interfaces', backref="children", remote_side=[id])

    def __repr__(self):
        return '<Interface name %r>' % self.interface_name


class Platforms(db.Model):
    __tablename__ = 'platforms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True, nullable=False)
    desc = db.Column(db.String(200))
    status = db.Column(db.SmallInteger, default=1, index=True)
    type = db.Column(db.String(20), default='backbone', index=True)
    domains = db.relationship('Domains', backref='domain_platform', lazy='dynamic')
    lines = db.relationship('LineDataBank', backref='line_platform', foreign_keys='LineDataBank.platform',
                            lazy='dynamic')
    lines_man_a = db.relationship("LineDataBank", backref='line_man_platform_a',
                                  foreign_keys='LineDataBank.MAN_platform_a',
                                  lazy='dynamic')
    lines_man_z = db.relationship("LineDataBank", backref='line_man_platform_z',
                                  foreign_keys='LineDataBank.MAN_platform_z',
                                  lazy='dynamic')
    devices = db.relationship('Device', backref='device_platform', lazy='dynamic')


class Domains(db.Model):
    __tablename__ = 'domains'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, index=True)
    platform = db.Column(db.Integer, db.ForeignKey('platforms.id'), index=True)
    owner_block_interface = db.Column(db.Integer, db.ForeignKey('interfaces.id'))
    neighbor_block_interface = db.Column(db.Integer, db.ForeignKey('interfaces.id'))
    status = db.Column(db.SmallInteger, default=1)

    def __init__(self, name, platform):
        self.name = name
        self.platform = platform


class LineDataBank(db.Model):
    __tablename__ = 'line_data_bank'
    id = db.Column(db.Integer, primary_key=True)
    line_code = db.Column(db.String(50), index=True)
    sub_line_code = db.Column(db.SmallInteger, default=1, index=True)
    customer = db.Column(db.Integer, db.ForeignKey('customer.id'), index=True, nullable=False)
    biz = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    noc = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    customer_manager = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    repair_code = db.Column(db.String(20))
    # 大类，例如传统业务
    product_type = db.Column(db.String(20), index=True)
    # dplc/ix/vxlan/dca/sdwan/line_rent/wave_rent
    product_model = db.Column(db.String(20), index=True, default='dplc')
    cloud_attribute = db.relationship("Cloud", backref='line_cloud', lazy='dynamic')
    mpls_attribute = db.relationship("MPLS", backref='line_mpls', lazy='dynamic')
    dia_attribute = db.relationship("DIA", backref='line_dia', lazy='dynamic')
    vxlan_attribute = db.relationship("VXLAN", backref='line_vxlan', lazy='dynamic')
    wave_attribute = db.relationship("WaveRent", backref='line_wave', lazy='dynamic')
    # 关联附件
    attached_files = db.relationship("Cloud", backref='file_belong_to', lazy='dynamic')
    # 参见line_status_dict 来自OSS, 默认100，表示为自建线路资源记录，非来自OSS
    line_status = db.Column(db.SmallInteger, index=True, default=100)
    # 1 normal; 2 变更； 3 删除
    record_status = db.Column(db.SmallInteger, default=1, index=True)

    # 表示a端客户实际地址，一般由OSS同步得到
    a_client_addr = db.Column(db.String(200), index=True)
    a_pop_interface = db.Column(db.Integer, db.ForeignKey('interfaces.id'), index=True)
    a_pop_type = db.Column(db.String(100))
    a_pop_interconnection = db.Column(db.Integer, db.ForeignKey('interconnection.id'))

    # 表示z端客户实际地址，一般由OSS同步得到
    z_client_addr = db.Column(db.String(200), index=True)
    z_pop_interface = db.Column(db.Integer, db.ForeignKey('interfaces.id'), index=True)
    z_pop_type = db.Column(db.String(100))
    z_pop_interconnection = db.Column(db.Integer, db.ForeignKey('interconnection.id'))

    # 1 bandwidth 2 optical cable
    channel_type = db.Column(db.SmallInteger, default=1, index=True)
    channel_number = db.Column(db.Integer, index=True)
    channel_unit = db.Column(db.String(20), default="G", index=True)

    protect = db.Column(db.Boolean, default=False, index=True)

    vlan = db.Column(db.Integer, db.ForeignKey('vlan.id'), index=True)

    main_route = db.Column(db.String(1000))
    main_e = db.Column(db.String(1000))
    backup_route = db.Column(db.String(1000))
    a_chain = db.Column(db.String(1000))
    a_e = db.Column(db.String(1000))
    z_chain = db.Column(db.String(1000))
    z_e = db.Column(db.String(1000))

    line_operator = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    operate_time = db.Column(db.DateTime, index=True)
    memo = db.Column(db.String(500))
    parent_id = db.Column(db.Integer, default=0, index=True)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, index=True)
    line_stop_time = db.Column(db.DateTime, index=True)
    # 2 not check yet 1 success 0 fail
    validate_rrpp_status = db.Column(db.SmallInteger, default=2, index=True)
    platform = db.Column(db.Integer, db.ForeignKey('platforms.id'), index=True)
    domains = db.relationship('Domains', secondary=lines_domains, backref=db.backref('lines'))
    posts = db.relationship('Post', backref='line_posts', lazy='dynamic')
    line_desc = db.Column(db.String(1000))
    __table_args__ = (UniqueConstraint('line_code', 'sub_line_code', name='_line_code_combine'),)
    # 城网只有domain的概念，此处沿用platform对应domain的概念，这里的platform为可为上海城网、北京城网
    MAN_platform_a = db.Column(db.Integer, db.ForeignKey('platforms.id'), index=True)
    MAN_domains_a = db.relationship('Domains', secondary=man_lines_domains_a, backref=db.backref('man_lines_a'))
    MAN_platform_z = db.Column(db.Integer, db.ForeignKey('platforms.id'), index=True)
    MAN_domains_z = db.relationship('Domains', secondary=man_lines_domains_z, backref=db.backref('man_lines_z'))

    def __repr__(self):
        return '<Line code  %r>' % self.line_code


class DNSManager(db.Model):
    """
    用于管理DNS
    """
    __tablename = 'dns_manager'
    id = db.Column(db.Integer, primary_key=True)
    dns = db.Column(db.String(48), index=True, nullable=False, default='114.114.114.114')
    dns_role = db.Column(db.String(10), default='master', index=True)
    dia_dns = db.relationship('DIA', backref='isp_dns')
    ip_id = db.relationship('IPManager', backref='ip_dns')

    def __repr__(self):
        return '<DNS %r>' % self.dns


class IPSupplier(db.Model):
    __tablename__ = "ip_supplier"
    id = db.Column(db.Integer, primary_key=True)
    line_code = db.Column(db.String(48), unique=True, index=True, nullable=False)
    supplier_name = db.Column(db.Integer, db.ForeignKey('customer.id'), index=True, nullable=False)
    line_access_interface = db.Column(db.Integer, db.ForeignKey('interfaces.id'))
    # 1 网关模式 2 路由模式
    mode = db.Column(db.SmallInteger, default=1)
    bandwidth = db.Column(db.Float)
    bandwidth_unit = db.Column(db.String(5), default='G')
    interconnect_ip = db.Column(db.Integer, db.ForeignKey('ip_manager.id'))
    available_ip = db.Column(db.Integer, db.ForeignKey('ip_group.id'))
    vlan = db.Column(db.Integer, db.ForeignKey('vlan.id'))
    start_time = db.Column(db.DateTime)
    stop_time = db.Column(db.DateTime)
    # 1 表示状态正常
    status = db.Column(db.SmallInteger, default=1)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    biz = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    noc = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    customer_manager = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    line_operator = db.Column(db.Integer, db.ForeignKey('users.id'))
    operate_time = db.Column(db.DateTime)


class IPGroup(db.Model):
    __tablename__ = "ip_group"
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(100), default='default')
    ip_list = db.relationship("IPManager", backref='group', lazy='dynamic')
    mpls_ip = db.relationship("MPLS", backref='mpls_interconnect_ip', lazy='dynamic',
                              foreign_keys='MPLS.interconnect_ip')
    mpls_route = db.relationship("MPLS", backref='mpls_route_ip', lazy='dynamic', foreign_keys='MPLS.local_route')
    ip_supplier = db.relationship("IPSupplier", backref='available_ip_group', lazy='dynamic')
    ip_dia = db.relationship("DIA", backref='available_dia_ip', lazy='dynamic')


class IPManager(db.Model):
    """
    用于管理IP地址段
    """
    __tablename__ = 'ip_manager'
    id = db.Column(db.Integer, primary_key=True)
    IP = db.Column(db.String(48), index=True, nullable=False)
    netmask = db.Column(db.String(3), index=True, nullable=False, default='32')
    gateway = db.Column(db.String(48), index=True)
    available_ip = db.Column(db.String(500))
    desc = db.Column(db.String(100))
    # 指IP真实的ISP，例如电信、联通、移动
    isp = db.Column(db.String(100))
    dia_ip = db.relation("DIA", backref='isp_ip', lazy='dynamic', foreign_keys='DIA.ip')
    ip_group = db.Column(db.Integer, db.ForeignKey('ip_group.id'), index=True)
    ip_supplier = db.relationship("IPSupplier", backref='ip_a_z', lazy='dynamic')
    dns = db.Column(db.Integer, db.ForeignKey('dns_manager.id'), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('ip_manager.id'))
    parent = db.relationship('IPManager', backref="children", remote_side=[id])


class Cloud(db.Model):
    """
    用于云接入业务，例如DCA， SDWAN等
    """
    __tablename__ = 'cloud'
    id = db.Column(db.Integer, primary_key=True)
    cloud_provider = db.Column(db.String(10), index=True, nullable=False)
    cloud_accesspoint = db.Column(db.String(50), index=True, nullable=False)
    cloud_accesspoint_desc = db.Column(db.String(200))
    line_id = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))

    def __repr__(self):
        return '<Cloud provider name %r>' % self.cloud_provider


class WaveRent(db.Model):
    """
    用于波道业务
    """
    __tablename__ = 'wave_rent'
    id = db.Column(db.Integer, primary_key=True)
    wave = db.Column(db.String(10), nullable=False)
    route = db.Column(db.String(1000))
    line_id = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))


class DIA(db.Model):
    """
    用于带宽业务
    """
    __tablename__ = 'dia'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.Integer, db.ForeignKey('ip_manager.id'))
    available_ip = db.Column(db.Integer, db.ForeignKey('ip_group.id'))
    dns = db.Column(db.Integer, db.ForeignKey('dns_manager.id'))
    provider = db.Column(db.String(100))
    line_id = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))
    # 1 网关模式 通过互联地址将IP推送给用户，需要供应商是路由模式
    # 2 路由模式 通过互联地址，写静态路由将IP推送给用户，需要供应商是路由模式
    # 3 透传模式 没有互联地址，供应商是网关模式
    # 4 NAT模式  运营商一般为网关模式，也可以是路由模式，需要和用户有互联地址
    mode = db.Column(db.SmallInteger, default=1)


class VXLAN(db.Model):
    __tablename__ = 'vxlan'
    id = db.Column(db.Integer, primary_key=True)
    bd = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(100))
    line_id = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))


class MPLS(db.Model):
    """
    用于MPLS业务特有属性
    """
    __tablename__ = 'mpls'
    id = db.Column(db.Integer, primary_key=True)
    route_protocol = db.Column(db.String(20), default='static')
    as_number = db.Column(db.Integer)
    access_way = db.Column(db.String(10), default='专线')
    vrf = db.Column(db.String(100))
    rt = db.Column(db.String(10))
    line_id = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))
    interconnect_ip = db.Column(db.Integer, db.ForeignKey('ip_group.id'))
    local_route = db.Column(db.Integer, db.ForeignKey('ip_group.id'))


class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(20), unique=True, index=True, nullable=False)
    country = db.Column(db.String(20), default='中国')
    machine_room = db.relationship('MachineRoom', backref='cities', lazy='dynamic')


class MachineRoom(db.Model):
    __tablename__ = 'machineroom_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24), unique=True, nullable=False)
    city = db.Column(db.Integer, db.ForeignKey('city.id'), index=True, nullable=False)
    address = db.Column(db.String(100), unique=True, nullable=False)
    # 1 业务站 2 光放站
    level = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Integer, nullable=False, default=1)
    permit_value = db.Column(db.String(200))
    devices = db.relationship('Device', backref='machine_room', lazy='dynamic')
    noc_contact = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    lift = db.Column(db.Boolean, default=False)
    # 1: 自建； 2： 缆信； 3： 第三方
    type = db.Column(db.SmallInteger, default=1)

    def __repr__(self):
        return '<Machine Room %r>' % self.name


class Device(db.Model):
    __tablename__ = 'device_list'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(200))
    device_belong = db.Column(db.Integer, db.ForeignKey('customer.id'))
    ip = db.Column(db.String(48), index=True, unique=True, nullable=False)
    login_method = db.Column(db.String(10), default='TELNET')
    login_name = db.Column(db.String(20))
    login_password = db.Column(db.String(20))
    enable_password = db.Column(db.String(20), nullable=True)
    machine_room_id = db.Column(db.Integer, db.ForeignKey('machineroom_list.id'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'))
    status = db.Column(db.Integer, nullable=False, default=1)
    community = db.Column(db.String(20), index=True)
    monitor_status = db.Column(db.SmallInteger)
    monitor_fail_date = db.Column(db.DateTime)
    # 恢复时间
    monitor_rec_date = db.Column(db.DateTime)
    mib_model = db.Column(db.SmallInteger)
    # 华为给HUAWEI  思科给CISCO 盛科给CENTEC
    vendor = db.Column(db.String(100), default="HUAWEI")
    # 2102350JAR6TJ8000446
    serial_number = db.Column(db.String(100))
    # 40EE-DD79-7EC1
    device_mac = db.Column(db.String(50))
    # V200R002C50SPC800
    os_version = db.Column(db.String(50))
    # V200R002SPH013
    patch_version = db.Column(db.String(50))
    # CE6851HI
    device_model = db.Column(db.String(50))
    interface = db.relationship('Interfaces', backref='device_interface', lazy='dynamic')

    def __repr__(self):
        return '<device name %r>' % self.device_name


class SnmpInterface(db.Model):
    __tablename__ = 'snmp_interface'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, index=True)
    snmp_sysname = db.Column(db.String(100))
    snmp_if_desc = db.Column(db.String(50), index=True)
    snmp_if_alias = db.Column(db.String(200))
    snmp_if_physical_status = db.Column(db.SmallInteger)
    snmp_if_protocol_status = db.Column(db.SmallInteger)
    snmp_last_down_time = db.Column(db.DateTime)
    snmp_last_rec_time = db.Column(db.DateTime)
    snmp_last_in_speed = db.Column(db.Float)
    snmp_last_out_speed = db.Column(db.Float)
    data_storage = db.Column(db.String(100), default='redis')
    data_path = db.Column(db.String(100), default='10')
    snmp_last_fetch_status = db.Column(db.String(100), default='Success')
    update_time = db.Column(db.DateTime)


class SnmpModels(db.Model):
    __tablename__ = 'snmp_models'
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100), index=True)
    device_type = db.Column(db.String(100))
    oid_name = db.Column(db.String(50))
    oid = db.Column(db.String(100))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'REGION': (Permission.FOLLOW |
                       Permission.COMMENT |
                       Permission.WRITE_ARTICLES |
                       Permission.MODERATE_COMMENTS |
                       Permission.REGION_SUPPORT, False),
            'MAN_ON_DUTY': (Permission.FOLLOW |
                            Permission.COMMENT |
                            Permission.WRITE_ARTICLES |
                            Permission.MODERATE_COMMENTS |
                            Permission.REGION_SUPPORT |
                            Permission.MAN_ON_DUTY, False),
            'SNOC': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES |
                     Permission.MODERATE_COMMENTS |
                     Permission.REGION_SUPPORT |
                     Permission.MAN_ON_DUTY |
                     Permission.NETWORK_MANAGER, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    alarm_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    line_id = db.Column(db.Integer, db.ForeignKey('line_data_bank.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        attrs = {
            '*': ['class'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt', 'width', 'height'],
        }
        target.body_html = bleach.clean(value, tags=allowed_tags, attributes=attrs, strip=True)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class ApiConfigure(db.Model):
    __tablename__ = 'api_configure'
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(20), nullable=False)
    api_params = db.Column(db.String(100), nullable=False)
    api_params_value = db.Column(db.String(200))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    phoneNum = db.Column(db.String(15), unique=True)
    username = db.Column(db.String(64), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    area = db.Column(db.Integer, db.ForeignKey('area.id'))
    duty = db.Column(db.Integer, db.ForeignKey('job_desc.job_id'))
    permit_machine_room = db.Column(db.String(200), index=True)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.SmallInteger)
    post = db.relationship('Post', backref='author', lazy='dynamic')
    lines = db.relationship('LineDataBank', backref='operator', lazy='dynamic')
    supplier = db.relationship('IPSupplier', backref='supplier_operator', lazy='dynamic')
    sms_order = db.relationship('SMSOrder', backref='sms_sender', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_moderate(self):
        return self.can(Permission.MODERATE_COMMENTS)

    def is_region(self):
        return self.can(Permission.REGION_SUPPORT)

    def is_manonduty(self):
        return self.can(Permission.MAN_ON_DUTY)

    def is_snoc(self):
        return self.can(Permission.NETWORK_MANAGER)

    def __repr__(self):
        return '<User %r>' % self.username


class AccountInfo(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, index=True)
    password = db.Column(db.String(40))
    interface = db.Column(db.String(10), index=True)
    sub_int = db.Column(db.String(5), index=True)
    ip = db.Column(db.String(20))
    mac = db.Column(db.String(30), index=True)
    bas_name = db.Column(db.String(20))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<ACCOUNT INFO -> USERNAME: %r>' % self.username


class AreaMachineRoom(db.Model):
    __tablename__ = 'area_machine_room'
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, index=True, nullable=False)
    permit_machine_room = db.Column(db.Integer, nullable=False)


class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(30), index=True, nullable=False)
    area_desc = db.Column(db.String(200))
    area_machine_room = db.Column(db.String(200))
    user = db.relationship('User', backref='user_area', lazy='dynamic')

    def __repr__(self):
        return '<Area info: %r>' % self.area_name


class CallRecordDetail(db.Model):
    __tablename__ = 'call_record_detail'
    id = db.Column(db.Integer, primary_key=True)
    phoneNum = db.Column(db.String(20), index=True)
    respCode = db.Column(db.String(10), index=True)
    callId = db.Column(db.String(40), index=True)
    createDateInResp = db.Column(db.String(15), index=True)
    create_time = db.Column(db.DateTime)
    call_group = db.Column(db.String(32), index=True)


class VoiceNotifyCallBack(db.Model):
    __tablename__ = 'voice_notify_callback'
    id = db.Column(db.Integer, primary_key=True)
    phoneNum = db.Column(db.String(15), index=True)
    state = db.Column(db.String(5))
    callId = db.Column(db.String(40))
    create_time = db.Column(db.DateTime)


class DutySchedule(db.Model):
    __tablename__ = 'duty_schedule'
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.Date)
    userid = db.Column(db.String(100), nullable=False)
    attended_time_id = db.Column(db.SmallInteger, nullable=False)
    duty_status = db.Column(db.SmallInteger, nullable=False)
    priority = db.Column(db.SmallInteger, nullable=False, default=0)
    create_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Duty schedule date: %r>' % self.date_time


class JobDescription(db.Model):
    __tablename__ = 'job_desc'
    job_id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(20))
    job_desc = db.Column(db.String(100))
    alarm_type = db.Column(db.String(20))


class DutyAttendedTime(db.Model):
    __tablename__ = 'duty_attended_time'
    id = db.Column(db.Integer, primary_key=True)
    attended_time_name = db.Column(db.String(64), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    stop_time = db.Column(db.Time, nullable=False)
    day_adjust = db.Column(db.SmallInteger, nullable=True, default=0)
    status = db.Column(db.SmallInteger, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Duty attended time name: %r>' % self.attended_time_name


class TokenRecord(db.Model):
    __tablename__ = 'token_record'
    unique_id = db.Column(db.String(128), primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    expire = db.Column(db.String(10))
    create_time = db.Column(db.DateTime)


class AlarmRecord(db.Model):
    __tablename__ = 'alarm_record'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    content_md5 = db.Column(db.String(32), index=True)
    alarm_type = db.Column(db.SmallInteger, nullable=True, default=0)
    alarm_level = db.Column(db.SmallInteger, nullable=True, default=1)
    state = db.Column(db.SmallInteger)
    lastCallId = db.Column(db.String(128), index=True)
    calledTimes = db.Column(db.SmallInteger)
    create_time = db.Column(db.DateTime)
    call_group = db.Column(db.String(32), index=True)


class UpsInfo(db.Model):
    __tablename__ = 'ups_info'
    id = db.Column(db.Integer, primary_key=True)
    oid_dict = db.Column(db.String(200))
    ip = db.Column(db.String(24))
    name = db.Column(db.String(20))
    vendeor = db.Column(db.String(20))
    community = db.Column(db.String(20))


class PonAlarmRecord(db.Model):
    __tablename__ = 'pon_alarm_record'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    ip = db.Column(db.String(64))
    frame = db.Column(db.String(2))
    slot = db.Column(db.String(2))
    port = db.Column(db.String(3))
    ontid = db.Column(db.String(3), default='PON')
    fail_times = db.Column(db.Integer)
    status = db.Column(db.SmallInteger)
    last_fail_time = db.Column(db.DateTime)
    last_recovery_time = db.Column(db.DateTime)
    alarmed_flag = db.Column(db.SmallInteger, default=0)
    create_time = db.Column(db.DateTime)


class CallTimeRange(db.Model):
    __tablename__ = 'call_time_range'
    id = db.Column(db.Integer, primary_key=True)
    range_name = db.Column(db.String(100))
    start_time = db.Column(db.Time, nullable=False)
    stop_time = db.Column(db.Time, nullable=False)
    day_adjust = db.Column(db.Integer, default=0)
    valid_alarm_type = db.Column(db.String(20))
    status = db.Column(db.SmallInteger, default=1)


class SyslogAlarmConfig(db.Model):
    __tablename__ = 'syslog_alarm_config'
    id = db.Column(db.Integer, primary_key=True)
    alarm_type = db.Column(db.String(10))
    alarm_name = db.Column(db.String(100))
    alarm_level = db.Column(db.String(10))
    alarm_status = db.Column(db.SmallInteger)
    alarm_keyword = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)


class Syslog(db.Model):
    __tablename__ = 'syslog'
    id = db.Column(db.Integer, primary_key=True)
    facility = db.Column(db.String(20))
    serverty = db.Column(db.String(20))
    device_ip = db.Column(db.String(40))
    logmsg = db.Column(db.String(600))
    logtime = db.Column(db.DateTime)


class AdditionalInfo(db.Model):
    # 用途改为存放附加告警信息
    __tablename__ = 'additional_info'
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.String(256), nullable=False)
    additional_info = db.Column(db.String(256))


class PiRegister(db.Model):
    __tablename__ = 'pi_register'
    sysid = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(50), index=True, nullable=False)
    times = db.Column(db.Integer, default=0)
    last_register_time = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger)

    def __repr__(self):
        return '<Pi Register: %r>' % self.sysid


class PcapOrder(db.Model):
    __tablename__ = 'pcap_order'
    id = db.Column(db.String(128), primary_key=True)
    account_id = db.Column(db.String(20), index=True, nullable=False)
    login_name = db.Column(db.String(50), index=True, nullable=False)
    username = db.Column(db.String(20), index=True, nullable=False)
    question_description = db.Column(db.String(1024))
    # status:
    # 0->this user hasn't bind to a Pi
    # 1->just created
    # 2->processing
    # 3->recapture
    # 4->order finished
    status = db.Column(db.SmallInteger, default=1)
    create_time = db.Column(db.DateTime)


class PcapResult(db.Model):
    __tablename__ = 'pcap_result'
    id = db.Column(db.String(128), primary_key=True)
    sysid = db.Column(db.String(100), index=True)
    pcap_order_id = db.Column(db.String(128), index=True)
    pcap_filepath = db.Column(db.String(200))
    r2d2_filepath = db.Column(db.String(200))
    result_description = db.Column(db.String(1024))
    speedtest = db.Column(db.String(50))
    pingtest = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

alarm_record_state = {1: '呼叫失败',
                      2: '未定义',
                      3: '被叫未接听',
                      8: '已达最大呼叫次数, 并且未接听',
                      9: '呼叫成功',
                      99: '未呼叫'}

duty_schedule_status = {1: '正常',
                        2: '调休',
                        3: '事假',
                        4: '调班',
                        # 5: '加班',
                        6: '管理员删除',
                        7: '新增'}

ALLOWED_EXTENSIONS = {'pcap', 'pcapng'}

syslog_serverty = {0: "emergency",
                   1: "alert",
                   2: "critical",
                   3: "error",
                   4: "warning",
                   5: "notice",
                   6: "info",
                   7: "debug"
                   }
syslog_facility = {0: "kernel",
                   1: "user",
                   2: "mail",
                   3: "daemaon",
                   4: "auth",
                   5: "syslog",
                   6: "lpr",
                   7: "news",
                   8: "uucp",
                   9: "cron",
                   10: "authpriv",
                   11: "ftp",
                   12: "ntp",
                   13: "security",
                   14: "console",
                   15: "cron",
                   16: "local 0",
                   17: "local 1",
                   18: "local 2",
                   19: "local 3",
                   20: "local 4",
                   21: "local 5",
                   22: "local 6",
                   23: "local 7"
                   }
aes_key = 'koiosr2d2c3p0000'
max_ont_down_in_sametime = 4

temp_threshold = {'min': 20, 'max': 30}
humi_threshold = {'min': 15, 'max': 70}

line_status_dict = {1: '查询',
                    2: '待开通',
                    3: '开通',
                    4: '变更',
                    5: '测试',
                    6: '已完工',
                    7: '退线',
                    8: '撤单',
                    9: '完工中（客户经理补充金额信息）',
                    10: '完工中（账务核实完工信息）',
                    11: '退租完工中',
                    12: '已退完',
                    13: '待测试',
                    20: '废单（开通之前的订单可废单）'}

all_domains = ['domain1', 'domain2', 'domain3', 'domain4', 'domain5', 'domain6', 'domain7', 'domain8', 'domain9',
               'domain11', 'domain12', 'domain13', 'domain15', 'domain16', 'domain19', 'domain20', 'domain21',
               'domain22', 'domain23', 'domain25', 'domain26', 'domain27', 'domain30', 'domain31', 'domain32',
               'domain33', 'domain34', 'domain35', 'domain37', 'domain38', 'domain39']

multi_domains = [
    'domain5_domain15',
    'domain6_domain8',
    'domain5_domain38',
    'domain6_domain38',
    'domain12_domain15',
    'domain12_domain19',
    'domain12_domain21',
    'domain12_domain23',
    'domain12_domain30',
    'domain12_domain31',
    'domain12_domain33',
    'domain12_domain34',
    'domain12_domain35',
    'domain12_domain39',
    'domain26_domain31',
    'domain26_domain33',
    'domain26_domain34',
    'domain26_domain35',
    'domain26_domain39',
    'domain27_domain31',
    'domain27_domain33',
    'domain27_domain34',
    'domain27_domain35',
    'domain27_domain39'
]

erps_instance = ['ERPS1_2_5_7_9_11', 'ERPS3_4_6_7_10_12']

channel_type = {1: '带宽', 2: '裸纤', 9: '其它'}

status_dict = {'0': '已删除', '1': '运行中', '2': '待定'}
monitor_status = {1: "在线", 2: "离线"}

PermissionIP = ['127.0.0.1']

machineroom_level = {'1': '自建', '2': '缆信', '3': '第三方', '4': '城网'}

machineroom_type = {'1': '业务站', '2': '光放站'}

protect_desc_special_company = ['优刻得', '云朴']

Search_LineDataBank = [['客户名称', 'customer_name'],
                       ['线路编号', 'line_code'],
                       ['业务类型', 'product_model'],
                       ['线路内容', 'client_addr'],
                       ['通道', 'channel'],
                       ['vlan', 'vlan'],
                       ['平台及Domain', 'platform_domain'],
                       ['A-Z端', 'pop'],
                       ['路由', 'route'],
                       ['开通人', 'operator'],
                       ['客户', 'biz_noc'],
                       ['我司客户经理', 'customer_manager'],
                       ['线路描述', 'line_desc'],
                       ['文件名称', 'file_name'],
                       ['备注内容', 'memo']
                       ]

company_regex = re.compile('|'.join(protect_desc_special_company))

PATH_PREFIX = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE_PATH = PATH_PREFIX + 'config_file/'
UPLOAD_FOLDER = PATH_PREFIX + 'UploadFile/'
CACTI_PIC_FOLDER = PATH_PREFIX + '/static/cacti_pic/'

MailTemplet_Path_Temp = os.path.join(PATH_PREFIX, 'static/mail_templet/temp')

Cutover_Path_Temp = os.path.join(PATH_PREFIX, 'static/cutover/temp')

MailTemplet_Path = os.path.join(PATH_PREFIX, 'static/mail_templet')

UploadFile_Path_Temp = os.path.join(PATH_PREFIX, 'static/upload_file/temp')

UploadFile_Path = os.path.join(PATH_PREFIX, 'static/upload_file/')

MailResult_Path = os.path.join(PATH_PREFIX, 'mail_result')

QRCode_PATH = os.path.join(PATH_PREFIX, 'static/qrcode_image')

Temp_File_Path = os.path.join(PATH_PREFIX, 'static/tmp_file/temp')

REQUEST_RETRY_TIMES = 1
REQUEST_RETRY_TIMES_PER_TIME = 1

API_URL = {"interface": "http://127.0.0.1:5222/interface",
           "device_info": "http://127.0.0.1:6666/devices",
           "verify_ring": "http://10.250.62.1:5111/check_rrpp",
           "ali_sms": "http://10.250.62.1:9998/sendsms"}

ACCESS_DOMAIN = "http://10.172.172.164:1111/assets/"
