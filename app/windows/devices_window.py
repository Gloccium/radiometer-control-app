import asyncio
import json
import aiohttp as aiohttp
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit
from qasync import asyncSlot, asyncClose


class DevicesWindow(QWidget):
    def __init__(self, settings_window, sending_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window
        self.sending_window = sending_window
        self.name = QLineEdit()
        self.description = QLineEdit()
        self.send_button = QPushButton('Добавить', self)
        self.configure_elements()

    def configure_elements(self):
        self.name.setPlaceholderText('Название')
        self.description.setPlaceholderText('Описание')
        self.send_button.clicked.connect(self.send)

    @asyncSlot()
    async def send(self):
        add_device_url = f'https://{self.settings_window.server_address.text()}/add-device'
        add_device_url = "https://localhost:7209/add-device"
        data = {
            "name": self.name.text(),
            "description": self.description.text(),
        }
        try:
            async with self.session.post(add_device_url, data=data) as r:
                pass
        except Exception as e:
            print(e)

        devices_url = f'https://{self.settings_window.server_address.text()}/devices'
        devices_url = "https://localhost:7209/devices"
        try:
            async with self.session.get(devices_url) as r:
                self.sending_window.devices = json.loads(await r.read())
                self.sending_window.update()
        except Exception as e:
            print(e)

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()