import asyncio
import json
import aiohttp as aiohttp
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QDateEdit, QComboBox
from qasync import asyncSlot, asyncClose


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
        self.sex.insertItem(0, 'М')
        self.sex.insertItem(1, 'Ж')
        self.send_button.clicked.connect(self.send)

    @asyncSlot()
    async def send(self):
        add_patient_url = f'https://{self.settings_window.server_address.text()}/add-patient'
        add_patient_url = "https://localhost:7209/add-patient"
        data = {
            "name": self.name.text(),
            "surname": self.surname.text(),
            "patronymic": self.patronymic.text(),
            "birthDate": self.birth_date.dateTime().toString("yyyy-MM-dd"),
            "sex": self.sex.currentIndex(),
            "notes": self.notes.text()
        }
        try:
            async with self.session.post(add_patient_url, data=data) as r:
                pass
        except Exception as e:
            print(e)

        patients_url = f'https://{self.settings_window.server_address.text()}/patients'
        patients_url = "https://localhost:7209/patients"
        try:
            async with self.session.get(patients_url) as r:
                self.sending_window.patients = json.loads(await r.read())
                self.sending_window.update()
        except Exception as e:
            print(e)

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()