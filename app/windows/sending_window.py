import os

import requests
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QTimeEdit, QDateEdit


class SendingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.url = "https://localhost:7209/upload-measurement"
        self.surname_input = QLineEdit(self)
        self.surname_input.setPlaceholderText('Фамилия')
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Имя')
        self.patronymic_input = QLineEdit(self)
        self.patronymic_input.setPlaceholderText('Отчество')
        self.date_input = QDateEdit()
        self.time_input = QTimeEdit()
        self.patient_input = QLineEdit(self)
        self.patient_input.setPlaceholderText('Пациент')
        self.device_input = QLineEdit(self)
        self.device_input.setPlaceholderText('Устройство')
        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText('Описание')
        self.send_button = QPushButton('Отправить', self)
        self.send_button.clicked.connect(self.send)

    def send(self):
        files = {'file': open(os.path.abspath(os.path.join(__file__, "../../../data")), 'rb')}
        data = {
            "surname": self.surname_input.text(),
            "name": self.name_input.text(),
            "patronymic": self.patronymic_input.text(),
            "time": f'{self.date_input.dateTime().toString("yyyy-MM-dd")} {self.time_input.time().toString("hh:mm:ss")}',
            "patient": self.patient_input.text(),
            "device": self.device_input.text(),
            "description": self.description_input.text()
        }
        r = requests.post(self.url, verify=False, files=files, data=data)
