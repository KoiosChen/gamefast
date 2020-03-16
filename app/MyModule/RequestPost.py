# Excute result call back
import requests
from .. import logger, request_q, redis_db
from ..models import REQUEST_RETRY_TIMES, REQUEST_RETRY_TIMES_PER_TIME
from ..common import success_return, false_return
import threading
import time
import json


class StartThread(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.queue = q

    def run(self):
        while True:
            try:
                cb_success = False
                cb = self.queue.get()
                logger.debug(f"start to request order number {cb['value']['order_number']}")
                if 'retry' not in cb.keys():
                    cb['retry'] = 0
                else:
                    cb['retry'] += 1

                if cb['retry'] < REQUEST_RETRY_TIMES:
                    for i in range(0, REQUEST_RETRY_TIMES_PER_TIME):
                        # 此处用json.dumps之后，发送出去的，在python中才能用request.json方法来获取
                        try:
                            result = requests.post(cb['url'],
                                                   data=json.dumps(cb['value'], ensure_ascii=False).encode('utf-8'),
                                                   headers=cb['headers'])
                            r = result.json()
                            logger.debug(f'The response of this request is {r}')
                            if r.get('code') == 'true':
                                cb_success = True
                                break
                            else:
                                time.sleep(3)
                        except Exception as e:
                            logger.debug(f"Response error {e}")
                            time.sleep(3)
                            request_q.put(cb)
                    if not cb_success:
                        request_q.put(cb)
                self.queue.task_done()
            except Exception as e:
                logger.error("request post fail for {}".format(e))


# 在manager中启动回调线程池
def request_worker(thread_num=1):
    """
    用来调度获取建议书任务，线程池默认共1个线程
    :return:
    """

    for threads_pool in range(thread_num):
        t = StartThread(request_q)
        t.setDaemon(True)
        t.start()


# AllocateWorker调用call_back方法，把需要回调的数据put到队列里
def post_request(url, value, request_lock="_no_request_lock_"):
    headers = {'Content-Type': 'application/json', "encoding": "utf-8", 'Cache-Control': 'no-store'}

    if not redis_db.exists(request_lock):
        # 如果请求要求锁定，则写入Redis中
        if request_lock is not None and request_lock != "_no_request_lock_":
            redis_db.set(request_lock, 1, ex=300)

        request_q.put({'headers': headers,
                       'url': url,
                       'value': value,
                       'request_lock': request_lock})
        logger.info('{} has been put in the request queue'.format(value))
        return success_return("", '{} has been put in the request queue'.format(value))
    else:
        return false_return("", f"{request_lock} is locked")

