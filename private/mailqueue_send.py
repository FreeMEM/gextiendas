# -*- coding: utf-8 -*-
## in file /tuvozlegal/private/mailqueue_send.py

from gluon import *
from applications.gextiendas.modules.queuemail import Queuemail


def sendmessages():
	queuemail=Queuemail(db)
	queuemail.sendmessages()


sendmessages()
