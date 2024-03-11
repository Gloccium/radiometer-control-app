import base64
import json

from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QListWidget, QListWidgetItem

from app.utils.calibration_validation import validate_calibration
from app.widgets.list_adapter_widget.double_list_adapter_widget import DoubleListAdapter


class DeviceSelectionWindow(QWidget):
    def __init__(self, graph_window, settings_window, sending_window):
        super().__init__()
        self.setFixedSize(800, 600)
        self.graph_window = graph_window
        self.settings_window = settings_window
        self.sending_window = sending_window

        self.filtered_devices = []
        self.filtered_calibrations = []

        self.layout = QVBoxLayout(self)
        self.device = QLineEdit(self)
        self.device_list = QListWidget()

        self.calibration = QLineEdit(self)
        self.calibration_list = QListWidget()

        self.configure_elements()
        self.filter_device_list()
        self.set_previous_device()

    def select_device(self):
        if self.filtered_devices[self.device_list.currentRow()]["Id"] != self.graph_window.selected_device:
            self.graph_window.selected_calibration = None
            self.graph_window.calibration_data = None
        self.graph_window.selected_device = self.filtered_devices[self.device_list.currentRow()]["Id"]
        self.filter_calibration_list()

    def select_calibration(self):
        data = base64.b64decode(self.filtered_calibrations[self.calibration_list.currentRow()]["Data"])
        if validate_calibration(data, self.settings_window.locale):
            self.graph_window.selected_calibration = self.filtered_calibrations[self.calibration_list.currentRow()]["Id"]
            self.graph_window.calibration_data = json.loads(data)
        else:
            self.graph_window.selected_calibration = None
            self.graph_window.calibration_data = None
            self.calibration_list.setCurrentRow(-1)

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

    def filter_calibration_list(self):
        self.filtered_calibrations = []
        for calibration in self.graph_window.calibrations:
            if (self.calibration.text().lower() in calibration["Name"].lower()
                or self.calibration.text().lower() in calibration["Description"].lower()) \
                    and calibration["DeviceId"] == self.graph_window.selected_device:
                self.filtered_calibrations.append(calibration)
        self.update_calibration_list()

    def update_calibration_list(self):
        self.calibration_list.clear()
        for calibration in self.filtered_calibrations:
            list_adapter = DoubleListAdapter(name='Название', description='Описание')
            list_adapter.set_name(calibration["Name"])
            list_adapter.set_description(calibration["Description"])

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.calibration_list.addItem(list_adapter_item)
            self.calibration_list.setItemWidget(list_adapter_item, list_adapter)

    def set_previous_device(self):
        device_index, calibration_index = None, None

        for i in range(len(self.filtered_devices)):
            if self.graph_window.selected_device == self.filtered_devices[i]["Id"]:
                device_index = i
        if device_index is not None:
            self.device_list.setCurrentRow(device_index)
            self.filter_calibration_list()

        for i in range(len(self.filtered_calibrations)):
            if self.graph_window.selected_calibration == self.filtered_calibrations[i]["Id"]:
                calibration_index = i
        if calibration_index is not None:
            self.calibration_list.setCurrentRow(calibration_index)

    def configure_elements(self):
        self.device.setPlaceholderText('Введите название или описание устройства')
        self.calibration.setPlaceholderText('Введите название или описание калибровки')

        self.layout.addWidget(self.device)
        self.layout.addWidget(self.device_list)
        self.layout.addWidget(self.calibration)
        self.layout.addWidget(self.calibration_list)

        self.device.textChanged.connect(self.filter_device_list)
        self.device_list.clicked.connect(self.select_device)

        self.calibration.textChanged.connect(self.filter_calibration_list)
        self.calibration_list.clicked.connect(self.select_calibration)
