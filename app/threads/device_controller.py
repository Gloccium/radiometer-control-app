import asyncio
from asyncio import new_event_loop
from queue import Queue

from PyQt5.QtCore import QObject
from serial import Serial
from serial_asyncio import open_serial_connection


class DeviceController(QObject):
    def __init__(self):
        super().__init__()
        self.port = ""
        self.baudrate = 9600
        self.channel_data = Queue()
        self.reader = None
        self.writer = None
        self.loop = None

    def load_data(self) -> None:
        self.loop = new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run())

    def clear_data(self):
        self.channel_data = Queue()

    async def run(self) -> None:
        serial = Serial(self.port)
        serial.reset_input_buffer()
        serial.close()
        self.reader, self.writer = await open_serial_connection(url=self.port, baudrate=self.baudrate)
        while True:
            packet = await self.reader.readline()
            self.channel_data.put(packet)
