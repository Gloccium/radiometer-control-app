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
from app.windows.patient_window import PatientWindow


class SendingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.patients_window = None

        self.settings_window = None
        self.graph_window = None

        self.is_authentificated = False
        self.token = ''
        self.user_id = None

        self.patients = []
        self.filtered_patients = []
        self.selected_patient_index = None

        self.login = QLineEdit()
        self.password = QLineEdit()

        self.date = QDateEdit()
        self.time = QTimeEdit()
        self.description = QLineEdit(self)
        self.patient = QLineEdit(self)
        self.patient_list = QListWidget()
        self.add_patient_button = QPushButton('Добавить пациента', self)
        self.send_measurement_button = QPushButton('Отправить', self)
        self.login_button = QPushButton('Войти', self)

        self.configure_elements()
        self.set_visibility()

    def configure_elements(self):
        self.login.setPlaceholderText('Логин')
        self.password.setPlaceholderText('Пароль')
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_button.clicked.connect(self.login_action)

        self.patient.setPlaceholderText('Введите ФИО или заметки о пациенте')
        self.description.setPlaceholderText('Описание')
        self.date.setDate(QDate.currentDate())
        self.send_measurement_button.clicked.connect(self.send_measurement)
        self.add_patient_button.clicked.connect(self.add_patient)
        self.patient.textChanged.connect(self.filter_patient_list)
        self.patient_list.clicked.connect(self.select_patient)

    def set_visibility(self):
        if self.is_authentificated:
            self.login.hide()
            self.password.hide()
            self.login_button.hide()

            self.date.show()
            self.time.show()
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
            self.patient.hide()
            self.patient_list.hide()
            self.add_patient_button.hide()
            self.description.hide()
            self.send_measurement_button.hide()

    def add_patient(self):
        self.patients_window = PatientWindow(self.settings_window, self)
        self.patients_window.show()

    def select_patient(self):
        self.selected_patient_index = self.patient_list.currentRow()

    def filter_patient_list(self):
        self.filtered_patients = []
        for patient in self.patients:
            if self.patient.text().lower() in (patient["Name"] + patient["Surname"] + patient["Patronymic"]).lower() \
                    or self.patient.text().lower() in patient["Notes"].lower():
                self.filtered_patients.append(patient)
        self.update_patient_list()

    def update_patient_list(self):
        self.patient_list.clear()
        for patient in self.filtered_patients:
            list_adapter = DoubleListAdapter(name='ФИО', description='Заметки')
            list_adapter.set_name(f'{patient["Name"]} {patient["Surname"]} {patient["Patronymic"]}')
            list_adapter.set_description(patient["Notes"])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.patient_list.addItem(list_adapter_item)
            self.patient_list.setItemWidget(list_adapter_item, list_adapter)

    @asyncSlot()
    async def send_measurement(self):
        if self.graph_window.selected_device is None or self.selected_patient_index is None or self.user_id is None:
            show_error(QMessageBox.Warning, "Неправильно заполенена форма", "Должны быть выбраны пациент и устройство")
            return

        add_measurement_url = f'https://{self.settings_window.server_address}/add-measurement'
        headers = {"Authorization": f'Bearer {self.token}'}
        data = {
            "time": f'{self.date.dateTime().toString("yyyy-MM-dd")} {self.time.time().toString("hh:mm:ss")}',
            'file': open(os.path.abspath(os.path.join(__file__, "../../../data")), 'rb'),
            "description": self.description.text(),
            "userId": str(self.user_id),
            "patientId": str(self.filtered_patients[self.selected_patient_index]["Id"]),
            "deviceId": str(self.graph_window.selected_device),
        }
        try:
            async with self.session.post(add_measurement_url, headers=headers, data=data, timeout=3) as r:
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

        login_url = f'https://{self.settings_window.server_address}/login'
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
        if authorization_data["value"]["access_token"] != '':
            self.token = authorization_data["value"]["access_token"]
            self.user_id = authorization_data["value"]["userId"]
            self.is_authentificated = True
            self.set_visibility()
            self.graph_window.set_visibility()
            self.graph_window.calibration_data = None
            await self.graph_window.update_devices()
            await self.graph_window.update_calibrations()
            await self.update_patients()

    @asyncSlot()
    async def update_patients(self):
        patients_url = f'https://{self.settings_window.server_address}/patients'
        headers = {"Authorization": f'Bearer {self.token}'}
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
