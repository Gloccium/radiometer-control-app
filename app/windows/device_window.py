import asyncio
import aiohttp as aiohttp
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QMessageBox
from qasync import asyncSlot, asyncClose

from app.const import BUTTON_HEIGHT
from app.utils.error_messages import show_error, is_network_error
from app.locales.locales import locales


class DeviceWindow(QWidget):
    def __init__(self, graph_window, settings_window, sending_window):
        super().__init__()
        self.setFixedSize(800, 600)
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.graph_window = graph_window
        self.settings_window = settings_window
        self.sending_window = sending_window
        self.layout = QVBoxLayout(self)
        self.name = QLineEdit(self)
        self.description = QLineEdit(self)
        self.send_button = QPushButton(self)
        self.configure_elements()
        self.set_texts()

    def configure_elements(self):
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.send_button)
        self.layout.addStretch()
        self.send_button.clicked.connect(self.send)
        self.send_button.setFixedHeight(BUTTON_HEIGHT)

    def set_texts(self):
        self.send_button.setText(locales[self.settings_window.locale]['add'])
        self.name.setPlaceholderText(locales[self.settings_window.locale]['name'])
        self.description.setPlaceholderText(locales[self.settings_window.locale]['description'])

    @asyncSlot()
    async def send(self):
        if self.name.text() == '':
            show_error(QMessageBox.Warning, locales[self.settings_window.locale]['form_filled_incorrectly'],
                       locales[self.settings_window.locale]['must_fill_name'])
            return

        add_device_url = f'https://{self.settings_window.server_address}/add-device'
        headers = {"Authorization": f'Bearer {self.sending_window.token}'}
        data = {
            "name": self.name.text(),
            "description": self.description.text(),
        }
        try:
            async with self.session.post(add_device_url, headers=headers, json=data, timeout=3) as r:
                if is_network_error(r.status, self.settings_window.locale):
                    return
        except Exception as e:
            show_error(QMessageBox.Critical, locales[self.settings_window.locale]['network_connection_error'],
                       locales[self.settings_window.locale]['could_not_establish_connection'])
            print(e)
            return

        self.graph_window.update_devices()

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()
