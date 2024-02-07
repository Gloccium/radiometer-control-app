import asyncio
import aiohttp as aiohttp
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QMessageBox
from qasync import asyncSlot, asyncClose

from app.utils.error_messages import show_error, is_network_error


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
        self.send_button = QPushButton('Добавить', self)
        self.configure_elements()

    def configure_elements(self):
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.send_button)
        self.layout.addStretch()
        self.name.setPlaceholderText('Название')
        self.description.setPlaceholderText('Описание')
        self.send_button.clicked.connect(self.send)

    @asyncSlot()
    async def send(self):
        if self.name.text() == '':
            show_error(QMessageBox.Warning, "Неправильно заполенена форма", "Название должно быть заполнено")
            return

        add_device_url = f'https://{self.settings_window.server_address}/add-device'
        headers = {"Authorization": f'Bearer {self.sending_window.token}'}
        data = {
            "name": self.name.text(),
            "description": self.description.text(),
        }
        try:
            async with self.session.post(add_device_url, headers=headers, json=data, timeout=3) as r:
                if is_network_error(r.status):
                    return
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка соединения", "Не удалось установить соединение с сервером")
            print(e)
            return

        self.graph_window.update_devices()

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()