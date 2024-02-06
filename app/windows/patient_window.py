import asyncio
import json

import aiohttp as aiohttp
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QDateEdit, QComboBox, QMessageBox
from aiohttp import ClientTimeout
from qasync import asyncSlot, asyncClose

from app.utils.error_message import show_error


class PatientWindow(QWidget):
    def __init__(self, settings_window, sending_window):
        super().__init__()
        self.setFixedSize(800, 600)
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window
        self.sending_window = sending_window
        self.layout = QVBoxLayout(self)
        self.name = QLineEdit(self)
        self.surname = QLineEdit(self)
        self.patronymic = QLineEdit(self)
        self.birth_date = QDateEdit(self)
        self.sex = QComboBox(self)
        self.notes = QLineEdit(self)
        self.send_button = QPushButton('Добавить', self)
        self.configure_elements()

    def configure_elements(self):
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.surname)
        self.layout.addWidget(self.patronymic)
        self.layout.addWidget(self.birth_date)
        self.layout.addWidget(self.sex)
        self.layout.addWidget(self.notes)
        self.layout.addWidget(self.send_button)
        self.layout.addStretch()
        self.name.setPlaceholderText('Имя')
        self.surname.setPlaceholderText('Фамилия')
        self.patronymic.setPlaceholderText('Отчество')
        self.notes.setPlaceholderText('Заметки')
        self.birth_date.setDate(QDate.currentDate())
        self.sex.insertItem(0, 'М')
        self.sex.insertItem(1, 'Ж')
        self.send_button.clicked.connect(self.send)

    @asyncSlot()
    async def send(self):
        if self.name.text() == '' or self.surname.text() == '' or self.birth_date.date() == QDate.currentDate():
            show_error(QMessageBox.Warning, "Неправильно заполенена форма", "Имя, фамилия и дата рождения должны быть заполнены")
            return

        add_patient_url = f'https://{self.settings_window.server_address}/add-patient'
        headers = {'Token': self.sending_window.token}
        data = {
            "name": self.name.text(),
            "surname": self.surname.text(),
            "patronymic": self.patronymic.text(),
            "birthDate": self.birth_date.dateTime().toString("yyyy-MM-dd"),
            "sex": self.sex.currentIndex(),
            "notes": self.notes.text()
        }
        try:
            async with self.session.post(add_patient_url, headers=headers, data=data, timeout=3) as r:
                if r.status != 200:
                    show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
                    return
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
            print(e)
            return

        self.sending_window.update_patients()

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()