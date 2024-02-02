from PyQt5.QtWidgets import QMessageBox


def show_error(icon, title, text):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec_()