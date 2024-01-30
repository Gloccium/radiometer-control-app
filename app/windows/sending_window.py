import asyncio
import os

import aiohttp
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QTimeEdit, QDateEdit, QListWidget, QListWidgetItem
from qasync import asyncSlot, asyncClose

from app.widgets.list_adapter_widget.list_adapter_widget import ListAdapter
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
        self.filtered_devices = []
        self.patients = []
        self.filtered_patients = []
        self.selected_device = None
        self.selected_patient = None

        self.date = QDateEdit()
        self.time = QTimeEdit()
        self.description = QLineEdit(self)
        self.patient = QLineEdit(self)
        self.patient_list = QListWidget()
        self.add_patient_button = QPushButton('Добавить пациента', self)
        self.device = QLineEdit(self)
        self.device_list = QListWidget()
        self.add_device_button = QPushButton('Добавить устройство', self)
        self.send_button = QPushButton('Отправить', self)

        self.configure_elements()

    def configure_elements(self):
        self.device.setPlaceholderText('Введите название или описание устройства')
        self.patient.setPlaceholderText('Введите ФИО или заметки о пациенте')
        self.description.setPlaceholderText('Описание')
        self.date.setDate(QDate.currentDate())
        self.send_button.clicked.connect(self.send)
        self.add_device_button.clicked.connect(self.add_device)
        self.add_patient_button.clicked.connect(self.add_patient)
        self.device.textChanged.connect(self.filter_device_list)
        self.patient.textChanged.connect(self.filter_patient_list)
        self.device_list.clicked.connect(self.select_device)
        self.patient_list.clicked.connect(self.select_patient)

    def add_device(self):
        self.device_window = DeviceWindow(self.settings_window, self)
        self.device_window.show()

    def add_patient(self):
        self.patients_window = PatientWindow(self.settings_window, self)
        self.patients_window.show()

    def select_device(self):
        self.selected_device = self.device_list.currentRow()

    def select_patient(self):
        self.selected_patient = self.patient_list.currentRow()

    def filter_device_list(self):
        self.filtered_devices = []
        for device in self.devices:
            if self.device.text().lower() in device["Name"].lower() \
                    or self.device.text().lower() in device["Description"].lower():
                self.filtered_devices.append(device)
        self.update_device_list()

    def filter_patient_list(self):
        self.filtered_patients = []
        for patient in self.patients:
            if self.patient.text().lower() in (patient["Name"] + patient["Surname"] + patient["Patronymic"]).lower() \
                    or self.patient.text().lower() in patient["Notes"].lower():
                self.filtered_patients.append(patient)
        self.update_patient_list()

    def update_device_list(self):
        self.device_list.clear()
        for device in self.filtered_devices:
            list_adapter = ListAdapter()
            list_adapter.set_name(device["Name"])
            list_adapter.set_description(device["Description"])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.device_list.addItem(list_adapter_item)
            self.device_list.setItemWidget(list_adapter_item, list_adapter)

    def update_patient_list(self):
        self.patient_list.clear()
        for patient in self.filtered_patients:
            list_adapter = ListAdapter()
            list_adapter.set_name(f'{patient["Name"]} {patient["Surname"]} {patient["Patronymic"]}')
            list_adapter.set_description(patient["Notes"])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.patient_list.addItem(list_adapter_item)
            self.patient_list.setItemWidget(list_adapter_item, list_adapter)

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
