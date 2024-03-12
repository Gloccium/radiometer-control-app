from PyQt5.QtWidgets import QMessageBox
from app.locales.locales import locales


def show_error(icon, title, text):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec_()


def is_network_error(status, locale):
    if status == 400:
        show_error(QMessageBox.Critical, locales[locale]['save_error'],
                   f"{locales[locale]['record_already_exist']}. {locales[locale]['error']} {status}")
        return True
    if status == 401:
        show_error(QMessageBox.Critical, locales[locale]['authorization_error'],
                   f"{locales[locale]['authorization_failed']}. {locales[locale]['error']} {status}")
        return True
    elif status != 200:
        print(status)
        show_error(QMessageBox.Critical, locales[locale]['network_error'], f"{locales[locale]['network_error']} {status}")
        return True
    return False
