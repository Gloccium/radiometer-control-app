import asyncio
import os
import aiohttp
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QTimeEdit, QDateEdit, QComboBox
from qasync import asyncSlot, asyncClose


class SendingWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window
        self.devices = []

        self.surname = QLineEdit(self)
        self.name = QLineEdit(self)
        self.patronymic = QLineEdit(self)
        self.date = QDateEdit()
        self.time = QTimeEdit()
        self.patient = QLineEdit(self)
        self.device = QComboBox(self)
        self.description = QLineEdit(self)
        self.send_button = QPushButton('Отправить', self)
        self.configure_elements()

    def configure_elements(self):
        self.surname.setPlaceholderText('Фамилия')
        self.name.setPlaceholderText('Имя')
        self.patronymic.setPlaceholderText('Отчество')
        self.patient.setPlaceholderText('Пациент')
        self.device.setPlaceholderText('Устройство')
        self.description.setPlaceholderText('Описание')
        self.device.setEditable(True)
        self.device.completer().setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.send_button.clicked.connect(self.send)

    def update(self):
        self.device.clear()
        self.device.addItems(['Устройство ' + d['Name'] for d in self.devices])

    @asyncSlot()
    async def send(self):
        upload_measurement_url = f'https://{self.settings_window.server_address.text()}/upload-measurement'
        upload_measurement_url = "https://localhost:7209/upload-measurement"
        data = {
            "surname": self.surname.text(),
            "name": self.name.text(),
            "patronymic": self.patronymic.text(),
            "time": f'{self.date.dateTime().toString("yyyy-MM-dd")} {self.time.time().toString("hh:mm:ss")}',
            "patient": self.patient.text(),
            "device": self.device.currentText(),
            "description": self.description.text(),
            'file': open(os.path.abspath(os.path.join(__file__, "../../../data")), 'rb')
        }
        try:
            async with self.session.post(upload_measurement_url, data=data) as r:
                pass
        except Exception as e:
            print(e)

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()