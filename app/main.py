import sys
from PyQt5.QtWidgets import QApplication
from application_window import ApplicationWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    application_window = ApplicationWindow()
    sys.exit(app.exec_())
