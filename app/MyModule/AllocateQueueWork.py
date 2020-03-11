import threading
from .. import logger, work_q, redis_db
from ..proccessing_data import datatable_action
import json
import uuid
from ..MyModule.py_scapy import do
from ..MyModule.HashContent import md5_content
import os
from ..models import LineDataBank


class StartThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.queue = q

    def run(self):
        while True:
            __work = self.queue.get()
            try:
                func = __work.get('function')
                logger.debug(f">>> Allocate {__work} in the thread")
                eval(func).oss_operator(**__work)
            except Exception as e:
                logger.error(str(e))
            finally:
                self.queue.task_done()


def allocate_worker(thread_num=100):
    """
    用来处理上传的抓包文件，线程池默认共1个线程
    :return:
    """

    for threads_pool in range(thread_num):
        t = StartThread(work_q)
        t.setDaemon(True)
        t.start()
