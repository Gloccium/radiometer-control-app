import sys
from PyQt5.QtWidgets import QApplication
from application_window import ApplicationWindow
import ctypes
import matplotlib
import google
import google.protobuf
import google.protobuf.descriptor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    application_window = ApplicationWindow()
    sys.exit(app.exec_())
