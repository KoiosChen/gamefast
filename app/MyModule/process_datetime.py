import datetime
from .. import logger


def format_daterange(date_range):
    # 整理传入的时间范围
    if date_range:
        start_time, stop_time = date_range.split(' - ')
        start_time = datetime.datetime.strptime(start_time.strip(), '%Y/%m/%d %H:%M:%S')
        stop_time = datetime.datetime.strptime(stop_time.strip(), '%Y/%m/%d %H:%M:%S')
        logger.debug(f'format date range start from {start_time} to {stop_time}')
    else:
        start_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
        stop_time = datetime.datetime(2100, 12, 31, 23, 59, 59)

    return start_time, stop_time
