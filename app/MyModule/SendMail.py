import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.header import Header
from .. import logger, redis_db


class sendmail:
    def __init__(self, **kwargs):
        self.HOST = kwargs.setdefault('host', "mail.nbl.net.cn")
        self.SUBJECT = kwargs.setdefault('subject', "report")
        self.TO = kwargs.setdefault('mail_to', redis_db.lrange("mail_to", 0, -1))
        self.BCC = kwargs.setdefault('mail_bcc', redis_db.lrange("mail_bcc", 0, -1))
        self.FROM = kwargs.setdefault('mail_from', "chenjinzhang@nbl.net.cn")
        self.PASSWD = kwargs.setdefault('mail_passwd', "Cjz123456")

    def addimg(self, src, imgid):
        with open(src, 'rb') as fp:
            msgImage = MIMEImage(fp.read())
        msgImage.add_header('Content-ID', imgid)

        return msgImage

    def addMsgText(self, *context):
        return MIMEText(*context)

    def addAttachFile(self, src):
        with open(src, 'rb') as fp:
            try:
                attach = MIMEApplication(fp.read())
                filename = src.split('/')[-1]
                attach.add_header('Content-Disposition', 'attachment', filename=filename)
                return attach
            except Exception as e:
                logger.error(f'>>> Attach file failed for {e}')
                return False

    def send(self, **kwargs):
        msg = MIMEMultipart()
        if kwargs.get('addimg'):
            logger.info("It's is a test")
            msg.attach(self.addimg("/Users/Peter/Desktop/中传授权.jpg", "weeklyabc"))

        if kwargs.get('addmsgtext'):
            msg.attach(kwargs.get('addmsgtext'))

        if kwargs.get('addattach'):
            for attachment in kwargs.get('addattach'):
                msg.attach(attachment)

        msg['Subject'] = Header(self.SUBJECT, "utf-8")
        msg['From'] = self.FROM
        msg['To'] = self.TO
        msg['BCc'] = self.BCC
        msg["Accept-Language"] = "zh-CN"
        msg["Accept-Charset"] = "ISO-8859-1,utf-8,gb2312"
        try:
            server = smtplib.SMTP(timeout=30)
            server.connect(self.HOST, "25")
            server.login(self.FROM, self.PASSWD)
            send_msg = msg.as_string()
            logger.info('************** mail content ***************\n')
            logger.debug(f'{send_msg}')
            to_ = self.TO if isinstance(self.TO, list) else [self.TO]
            bcc_ = self.BCC if isinstance(self.BCC, list) else [self.BCC]
            total_sent_to = to_ + bcc_
            logger.debug(total_sent_to)
            server.sendmail(self.FROM, to_ + bcc_, send_msg)
            server.quit()
            logger.info(f">>> It is success to send the mail to {str(total_sent_to)}!")
            return True
        except Exception as e:
            logger.info(f">>> It is failed to send the mail for {e}!")
            return False
