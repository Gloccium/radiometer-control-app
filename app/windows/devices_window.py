import json

import requests
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit


class DevicesWindow(QWidget):
    def __init__(self, settings_window, sending_window):
        super().__init__()
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
        self.send_button.clicked.connect(self.update)

    def send(self):
        url = f'https://{self.settings_window.server_address.text()}/add-device'
        url = "https://localhost:7209/add-device"
        data = {
            "name": self.name.text(),
            "description": self.description.text(),
        }
        r = requests.post(url, verify=False, data=data)

    def update(self):
        url = f'https://{self.settings_window.server_address.text()}/devices'
        url = "https://localhost:7209/devices"
        r = requests.get(url, verify=False)
        self.sending_window.devices = json.loads(r.content)
        self.sending_window.update()
