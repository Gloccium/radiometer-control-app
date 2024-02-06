import asyncio

import aiohttp as aiohttp
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QMessageBox, QDateEdit, QFileDialog, \
    QListWidget, QListWidgetItem
from qasync import asyncSlot, asyncClose

from app.utils.calibration_validation import validate_calibration
from app.utils.error_messages import show_error, is_network_error
from app.widgets.list_adapter_widget.double_list_adapter_widget import DoubleListAdapter


class CalibrationWindow(QWidget):
    def __init__(self, graph_window, settings_window, sending_window):
        super().__init__()
        self.setFixedSize(800, 600)
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.graph_window = graph_window
        self.settings_window = settings_window
        self.sending_window = sending_window

        self.selected_device_index = None
        self.calibration_file = None
        self.filtered_devices = []

        self.layout = QVBoxLayout(self)
        self.name = QLineEdit(self)
        self.filename = QLineEdit(self)
        self.file_browse_button = QPushButton('Выбрать файл', self)
        self.date = QDateEdit(self)
        self.description = QLineEdit(self)
        self.device = QLineEdit(self)
        self.device_list = QListWidget()
        self.send_button = QPushButton('Добавить', self)

        self.configure_elements()
        self.filter_device_list()

    def select_device(self):
        self.selected_device_index = self.device_list.currentRow()

    def filter_device_list(self):
        self.filtered_devices = []
        for device in self.graph_window.devices:
            if self.device.text().lower() in device["Name"].lower() \
                    or self.device.text().lower() in device["Description"].lower():
                self.filtered_devices.append(device)
        self.update_device_list()

    def update_device_list(self):
        self.device_list.clear()
        for device in self.filtered_devices:
            list_adapter = DoubleListAdapter(name='Название', description='Описание')
            list_adapter.set_name(device["Name"])
            list_adapter.set_description(device["Description"])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.device_list.addItem(list_adapter_item)
            self.device_list.setItemWidget(list_adapter_item, list_adapter)

    def open_file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            self.settings_window.calibration_directory_path
        )
        if filename != '':
            with open(filename, 'rb') as f:
                data = f.read()
                if validate_calibration(data):
                    self.filename.setText(filename)
                    self.calibration_file = data
                else:
                    self.filename.setText('')
                    self.calibration_file = None

    @asyncSlot()
    async def send(self):
        if self.name.text() == '' or self.calibration_file is None:
            show_error(QMessageBox.Warning, "Неправильно заполенена форма", "Название и файл не выбраны")
            return

        add_calibration_url = f'https://{self.settings_window.server_address}/add-calibration'
        headers = {"Authorization": f'Bearer {self.sending_window.token}'}
        data = {
            "name": self.name.text(),
            "date": self.date.dateTime().toString("yyyy-MM-dd"),
            'file': self.calibration_file,
            "description": self.description.text(),
            "deviceId": str(self.filtered_devices[self.selected_device_index]["Id"])
        }
        try:
            async with self.session.post(add_calibration_url, headers=headers, data=data, timeout=3) as r:
                if is_network_error(r.status):
                    return
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка соединения", "Не удалось установить соединение с сервером")
            print(e)
            return

        self.graph_window.update_calibrations()

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()

    def configure_elements(self):
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.date)
        self.layout.addWidget(self.filename)
        self.layout.addWidget(self.file_browse_button)
        self.layout.addWidget(self.description)
        self.layout.addWidget(self.device)
        self.layout.addWidget(self.device_list)
        self.layout.addWidget(self.send_button)
        self.layout.addStretch()
        self.name.setPlaceholderText('Название')
        self.device.setPlaceholderText('Введите название или описание устройства')
        self.description.setPlaceholderText('Описание')
        self.date.setDate(QDate.currentDate())
        self.filename.setDisabled(True)
        self.file_browse_button.clicked.connect(self.open_file_dialog)
        self.send_button.clicked.connect(self.send)
        self.device.textChanged.connect(self.filter_device_list)
        self.device_list.clicked.connect(self.select_device)
