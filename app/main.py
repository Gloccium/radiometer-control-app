import sys
from PyQt5.QtWidgets import QApplication
from app.application_window import ApplicationWindow
from app.messages import message_pb2
from application_window import ApplicationWindow
import ctypes
import matplotlib
import google.protobuf
import google.protobuf.descriptor
import serial_asyncio

if __name__ == '__main__':
    app = QApplication(sys.argv)
    application_window = ApplicationWindow()
    sys.exit(app.exec_())
