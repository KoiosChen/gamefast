import qrcode
import os
from ..models import QRCode_PATH, ACCESS_DOMAIN


def new_one(qr_content):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=20,
        border=4,
    )

    qr.add_data(ACCESS_DOMAIN + qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    filename = os.path.join(QRCode_PATH, qr_content + '.png')

    img.save(filename)

    return filename

