from queue import Queue

from PyQt5.QtCore import QObject
from serial import Serial

from app.helpers.reader import Reader


class DeviceController(QObject):
    def __init__(self):
        super().__init__()
        self.port = ""
        self.baudrate = 9600
        self.channel_data = Queue()
        self.serial = None
        self.is_running = False
        self.is_paused = False

    def stop(self):
        self.is_running = False

    def run(self) -> None:
        self.is_running = True
        self.serial = Serial(self.port, baudrate=self.baudrate)
        self.serial.reset_input_buffer()
        reader = Reader(self.serial)
        while self.is_running:
            if not self.is_paused:
                packet = reader.readline()
                self.channel_data.put(packet)
        self.serial.close()
        self.channel_data = Queue()
