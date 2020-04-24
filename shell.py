#!/usr/bin/env python
import os
from app import create_app, db
from app.models import Contacts, User, Role, MachineRoom, Device, City, LineDataBank, Customer, Vlan, Domains, \
    Platforms, IPGroup, IPSupplier, MPLS, Post, MailTemplet, CutoverOrder, DIA, Interfaces, IPManager, PATH_PREFIX, \
    SMSSendResult, SMSOrder
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

__author__ = 'Koios'

app = create_app(os.getenv('FLASK_CONFIG') or 'production')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Contacts=Contacts, User=User, Role=Role, MachineRoom=MachineRoom, City=City,
                Device=Device, LineDataBank=LineDataBank, Vlan=Vlan, IPSupplier=IPSupplier,
                IPGroup=IPGroup,
                Customer=Customer, MPLS=MPLS, Domains=Domains, Platforms=Platforms, Post=Post, MailTemplet=MailTemplet,
                CutoverOrder=CutoverOrder, DIA=DIA, Interfaces=Interfaces, IPManager=IPManager, PATH_PREFIX=PATH_PREFIX,
                SMSOrder=SMSOrder, SMSSendResult=SMSSendResult)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
