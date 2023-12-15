import asyncio
import time
from asyncio import new_event_loop
from PyQt5.QtCore import QObject
from serial_asyncio import open_serial_connection
from serial import SerialException


class DeviceController(QObject):
    def __init__(self):
        super().__init__()
        self.port = ""
        self.baudrate = 9600
        self.channel_data = []
        self.port_error = False

    def load_data(self):
        loop = new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run())

    async def run(self):
        try:
            reader, writer = await open_serial_connection(url=self.port, baudrate=self.baudrate)
            while True:
                packet = await reader.readline()
                self.channel_data.append(packet)
        except SerialException:
            self.port_error = True
