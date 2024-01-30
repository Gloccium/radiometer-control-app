import asyncio
import os
import aiohttp
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QTimeEdit, QDateEdit, QComboBox
from qasync import asyncSlot, asyncClose

from app.windows.device_window import DeviceWindow
from app.windows.patient_window import PatientWindow


class SendingWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window
        self.device_window = None
        self.patients_window = None

        self.devices = []
        self.patients = []

        self.date = QDateEdit()
        self.time = QTimeEdit()
        self.description = QLineEdit(self)
        self.patient = QComboBox(self)
        self.add_patient_button = QPushButton('Добавить пациента', self)
        self.device = QComboBox(self)
        self.add_device_button = QPushButton('Добавить устройство', self)
        self.send_button = QPushButton('Отправить', self)
        self.configure_elements()

    def configure_elements(self):
        self.device.setPlaceholderText('Устройство')
        self.description.setPlaceholderText('Описание')
        self.date.setDate(QDate.currentDate())
        self.device.setEditable(True)
        self.device.completer().setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.patient.setEditable(True)
        self.patient.completer().setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.send_button.clicked.connect(self.send)
        self.add_device_button.clicked.connect(self.add_device)
        self.add_patient_button.clicked.connect(self.add_patient)

    def add_device(self):
        self.device_window = DeviceWindow(self.settings_window, self)
        self.device_window.show()

    def add_patient(self):
        self.patients_window = PatientWindow(self.settings_window, self)
        self.patients_window.show()

    def update(self):
        self.device.clear()
        self.device.addItems([d['Name'] for d in self.devices])
        self.device.setCurrentText('')

        self.patient.clear()
        self.patient.addItems(f'{p["Name"]} {p["Surname"]}' for p in self.patients)
        self.patient.setCurrentText('')

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