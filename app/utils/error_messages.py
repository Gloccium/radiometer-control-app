from PyQt5.QtWidgets import QMessageBox


def show_error(icon, title, text):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec_()


def is_network_error(status):
    if status == 400:
        show_error(QMessageBox.Critical, "Ошибка сохранения",
                   f"Данная запись уже существует на сервере. Ошибка {status}")
        return True
    if status == 401:
        show_error(QMessageBox.Critical, "Ошибка авторизации",
                   f"Не удалось пройти авторизацию. Ошибка {status}")
        return True
    elif status != 200:
        print(status)
        show_error(QMessageBox.Critical, "Ошибка сети", f"Ошибка сети {status}")
        return True
    return False
