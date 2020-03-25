from . import db, logger, redis_db
from .models import CONFIG_FILE_PATH, QRCode_PATH, MailResult_Path, MailTemplet_Path, Temp_File_Path, UploadFile_Path, \
    Cutover_Path_Temp, MailTemplet_Path_Temp, UploadFile_Path_Temp, CACTI_PIC_FOLDER, UPLOAD_FOLDER
import os


def success_return(data="", msg=""):
    return {"code": "success", "data": data, "msg": msg}


def false_return(data="", msg=""):
    return {"code": "false", "data": data, "msg": msg}


def exp_return(data="", msg=""):
    return {"code": "exp", "data": data, "msg": msg}


def db_commit():
    try:
        db.session.commit()
        return success_return("", "db commit success")
    except Exception as e:
        logger.error(f"db commit error for {e}")
        db.session.rollback()
        return false_return("", f"db commit fail for {e}")


def init_mailto():
    """
    默认mail_to whnoc@nbl.net.cn，mail_bcc: chenjinzhang@nbl.net.cn
    """
    if not redis_db.exists('mail_to'):
        redis_db.lpush("mail_to", "whnoc@nbl.net.cn")
    if not redis_db.exists('mail_bcc'):
        redis_db.lpush("mail_bcc", "chenjinzhang@nbl.net.cn")


def init_path():
    """
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
    """
    for p in [CONFIG_FILE_PATH, UPLOAD_FOLDER, CACTI_PIC_FOLDER, MailTemplet_Path_Temp, Cutover_Path_Temp,
              MailTemplet_Path_Temp, MailTemplet_Path, UploadFile_Path_Temp, UploadFile_Path, MailResult_Path,
              QRCode_PATH, Temp_File_Path]:
        if not os.path.exists(p):
            os.makedirs(p)
