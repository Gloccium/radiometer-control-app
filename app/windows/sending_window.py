import asyncio
import json
import os

import aiohttp
from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QTimeEdit, QDateEdit, QListWidget, QListWidgetItem, \
    QMessageBox
from qasync import asyncSlot, asyncClose

from app.utils.error_message import show_error
from app.widgets.list_adapter_widget.double_list_adapter_widget import DoubleListAdapter
from app.windows.device_window import DeviceWindow
from app.windows.patient_window import PatientWindow


class SendingWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window
        self.device_window = None
        self.patients_window = None

        self.is_authentificated = False
        self.token = ''
        self.user_id = None

        self.devices = []
        self.filtered_devices = []
        self.patients = []
        self.filtered_patients = []
        self.selected_device = None
        self.selected_patient = None

        self.login = QLineEdit()
        self.password = QLineEdit()

        self.date = QDateEdit()
        self.time = QTimeEdit()
        self.description = QLineEdit(self)
        self.patient = QLineEdit(self)
        self.patient_list = QListWidget()
        self.add_patient_button = QPushButton('Добавить пациента', self)
        self.device = QLineEdit(self)
        self.device_list = QListWidget()
        self.add_device_button = QPushButton('Добавить устройство', self)
        self.send_measurement_button = QPushButton('Отправить', self)
        self.login_button = QPushButton('Войти', self)

        self.configure_elements()
        self.set_visibility()

    def configure_elements(self):
        self.login.setPlaceholderText('Логин')
        self.password.setPlaceholderText('Пароль')
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_button.clicked.connect(self.login_action)

        self.device.setPlaceholderText('Введите название или описание устройства')
        self.patient.setPlaceholderText('Введите ФИО или заметки о пациенте')
        self.description.setPlaceholderText('Описание')
        self.date.setDate(QDate.currentDate())
        self.send_measurement_button.clicked.connect(self.send_measurement)
        self.add_device_button.clicked.connect(self.add_device)
        self.add_patient_button.clicked.connect(self.add_patient)
        self.device.textChanged.connect(self.filter_device_list)
        self.patient.textChanged.connect(self.filter_patient_list)
        self.device_list.clicked.connect(self.select_device)
        self.patient_list.clicked.connect(self.select_patient)

    def set_visibility(self):
        if self.is_authentificated:
            self.login.hide()
            self.password.hide()
            self.login_button.hide()

            self.date.show()
            self.time.show()
            self.device.show()
            self.device_list.show()
            self.add_device_button.show()
            self.patient.show()
            self.patient_list.show()
            self.add_patient_button.show()
            self.description.show()
            self.send_measurement_button.show()
        else:
            self.login.show()
            self.password.show()
            self.login_button.show()

            self.date.hide()
            self.time.hide()
            self.device.hide()
            self.device_list.hide()
            self.add_device_button.hide()
            self.patient.hide()
            self.patient_list.hide()
            self.add_patient_button.hide()
            self.description.hide()
            self.send_measurement_button.hide()

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
            list_adapter = DoubleListAdapter()
            list_adapter.set_name(device["Name"])
            list_adapter.set_description(device["Description"])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.device_list.addItem(list_adapter_item)
            self.device_list.setItemWidget(list_adapter_item, list_adapter)

    def update_patient_list(self):
        self.patient_list.clear()
        for patient in self.filtered_patients:
            list_adapter = DoubleListAdapter()
            list_adapter.set_name(f'{patient["Name"]} {patient["Surname"]} {patient["Patronymic"]}')
            list_adapter.set_description(patient["Notes"])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.patient_list.addItem(list_adapter_item)
            self.patient_list.setItemWidget(list_adapter_item, list_adapter)

    @asyncSlot()
    async def send_measurement(self):
        if self.selected_device is None or self.selected_patient is None or self.user_id is None:
            show_error(QMessageBox.Warning, "Неправильно заполенена форма", "Должны быть выбраны пациент и устройство")
            return

        add_measurement_url = f'https://{self.settings_window.server_address.text()}/add-measurement'
        add_measurement_url = "https://localhost:7209/add-measurement"
        headers = {'Token': self.token}
        data = {
            "time": f'{self.date.dateTime().toString("yyyy-MM-dd")} {self.time.time().toString("hh:mm:ss")}',
            'file': open(os.path.abspath(os.path.join(__file__, "../../../data")), 'rb'),
            "description": self.description.text(),
            "userId": '2',
            "patientId": str(self.filtered_patients[self.selected_patient]["Id"]),
            "deviceId": str(self.filtered_devices[self.selected_device]["Id"]),
        }
        try:
            async with self.session.post(add_measurement_url, headers=headers, data=data) as r:
                if r.status != 200:
                    show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
                    return
        except Exception as e:
            print(e)
            return

    @asyncSlot()
    async def login_action(self):
        if self.login.text() == '' or self.password.text() == '':
            show_error(QMessageBox.Warning, "Неправильно заполенена форма", "Логин и пароль должны быть заполнены")
            return

        login_url = f'https://{self.settings_window.server_address.text()}/login'
        login_url = "https://localhost:7209/login"
        data = {
            "login": self.login.text(),
            "password": self.password.text()
        }
        try:
            async with self.session.post(login_url, data=data, timeout=3) as r:
                if r.status != 200:
                    show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
                    return
                data = await r.read()
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
            print(e)
            return

        authorization_data = json.loads(data)
        if authorization_data["token"] != '':
            self.token = authorization_data["token"]
            self.user_id = authorization_data["userId"]
            self.is_authentificated = True
            self.set_visibility()
            await self.update_devices()
            await self.update_patients()

    @asyncSlot()
    async def update_devices(self):
        devices_url = f'https://{self.settings_window.server_address.text()}/devices'
        devices_url = "https://localhost:7209/devices"
        headers = {'Token': self.token}
        try:
            async with self.session.get(devices_url, headers=headers, timeout=3) as r:
                if r.status != 200:
                    show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
                    return
                data = await r.read()
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
            print(e)
            return

        self.devices = json.loads(data)
        self.filter_device_list()

    @asyncSlot()
    async def update_patients(self):
        patients_url = f'https://{self.settings_window.server_address.text()}/patients'
        patients_url = "https://localhost:7209/patients"
        headers = {'Token': self.token}
        try:
            async with self.session.get(patients_url, headers=headers, timeout=3) as r:
                if r.status != 200:
                    show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
                    return
                data = await r.read()
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
            print(e)
            return

        self.patients = json.loads(data)
        self.filter_patient_list()

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()
