import sys
import asyncio
import qasync
import os
import base64
import jsonschema
import queue
import binascii
import time
import aiohttp
import datetime
import json
import ctypes
import matplotlib
import google.protobuf
import google.protobuf.descriptor
import serial_asyncio
import serial.tools
import serial.tools.list_ports
import scipy
import app

from scipy import signal
from PyQt5.QtWidgets import QApplication
from app.messages import message_pb2
from app.windows.application_window import ApplicationWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    application_window = ApplicationWindow()
    with loop:
        loop.run_forever()
    sys.exit(app.exec_())
