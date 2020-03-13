from . import db, logger


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
