import sys
from PyQt5.QtWidgets import QApplication
from app.messages import message_pb2
import ctypes
import matplotlib
import google.protobuf
import google.protobuf.descriptor
import serial_asyncio

from app.windows.application_window import ApplicationWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    application_window = ApplicationWindow()
    sys.exit(app.exec_())
