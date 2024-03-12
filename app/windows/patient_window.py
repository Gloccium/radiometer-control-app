import asyncio

import aiohttp as aiohttp
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QDateEdit, QComboBox, QMessageBox
from qasync import asyncSlot, asyncClose

from app.locales.locales import locales
from app.utils.error_messages import show_error, is_network_error


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
        self.send_button = QPushButton(self)
        self.configure_elements()
        self.set_texts()

    def configure_elements(self):
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.surname)
        self.layout.addWidget(self.patronymic)
        self.layout.addWidget(self.birth_date)
        self.layout.addWidget(self.sex)
        self.layout.addWidget(self.notes)
        self.layout.addWidget(self.send_button)
        self.layout.addStretch()
        self.birth_date.setDate(QDate.currentDate())
        self.sex.insertItem(0, '')
        self.sex.insertItem(1, '')
        self.send_button.clicked.connect(self.send)

    def set_texts(self):
        self.send_button.setText(locales[self.settings_window.locale]['add'])
        self.name.setPlaceholderText(locales[self.settings_window.locale]['patient_name'])
        self.surname.setPlaceholderText(locales[self.settings_window.locale]['surname'])
        self.patronymic.setPlaceholderText(locales[self.settings_window.locale]['patronymic'])
        self.notes.setPlaceholderText(locales[self.settings_window.locale]['notes'])
        self.sex.setItemText(0, locales[self.settings_window.locale]['male'])
        self.sex.setItemText(1, locales[self.settings_window.locale]['female'])

    @asyncSlot()
    async def send(self):
        if self.name.text() == '' or self.surname.text() == '' or self.birth_date.date() == QDate.currentDate():
            show_error(QMessageBox.Warning, locales[self.settings_window.locale]['form_filled_incorrectly'],
                       locales[self.settings_window.locale]['must_fill_first_and_last_name_and_birthdate'])
            return

        add_patient_url = f'https://{self.settings_window.server_address}/add-patient'
        headers = {"Authorization": f'Bearer {self.sending_window.token}'}
        data = {
            "name": self.name.text(),
            "surname": self.surname.text(),
            "patronymic": self.patronymic.text(),
            "birthDate": self.birth_date.dateTime().toString("yyyy-MM-dd"),
            "sex": self.sex.currentIndex(),
            "notes": self.notes.text()
        }
        try:
            async with self.session.post(add_patient_url, headers=headers, json=data, timeout=3) as r:
                if is_network_error(r.status, self.settings_window.locale):
                    return
        except Exception as e:
            show_error(QMessageBox.Critical, locales[self.settings_window.locale]['network_connection_error'],
                       locales[self.settings_window.locale]['could_not_establish_connection'])
            print(e)
            return

        self.sending_window.update_patients()

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()
