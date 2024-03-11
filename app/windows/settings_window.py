import json
import os

from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QFileDialog, QMessageBox, QLabel, QComboBox

from app.const import BUTTON_HEIGHT
from app.utils.error_messages import show_error
from app.utils.check_bound import check_bound
from app.widgets.bounds.graph_bounds import GraphBounds
from app.locales.locales import locales


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.server_address = ''
        self.records_directory_path = ''
        self.calibration_directory_path = ''
        self.min_delta_graph_value = None
        self.max_delta_graph_value = None
        self.min_channels_graph_value = None
        self.max_channels_graph_value = None
        self.locale = ''
        self.locales = ['ru', 'en']
        self.init_config_file()
        self.init_default_directories()
        self.load_configuration()
        self.server_address_label = QLabel(locales[self.locale]['server_address'])
        self.server_address_input = QLineEdit(self)
        self.records_directory = QLineEdit(self)
        self.records_directory_button = QPushButton('Выбрать директорию для исследований', self)
        self.calibration_directory = QLineEdit(self)
        self.calibration_directory_button = QPushButton('Выбрать директорию для калибровок', self)
        self.save_button = QPushButton('Сохранить', self)
        self.delta_graph_bounds = GraphBounds('Min графика температуры', 'Max графика температуры',
                                              self.min_delta_graph_value, self.max_delta_graph_value)
        self.channels_graph_bounds = GraphBounds('Min графика каналов', 'Max графика каналов',
                                                 self.min_channels_graph_value, self.max_channels_graph_value)
        self.locale_combobox = QComboBox(self)
        self.configure_elements()

    def select_records_directory(self):
        filename = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )
        if filename != '':
            self.records_directory_path = filename
            self.records_directory.setText(self.records_directory_path)

    def select_calibration_directory(self):
        filename = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )
        if filename != '':
            self.calibration_directory_path = filename
            self.calibration_directory.setText(self.calibration_directory_path)

    def save(self):
        self.server_address = self.server_address_input.text()
        self.records_directory_path = self.records_directory.text()
        try:
            os.makedirs(self.records_directory_path, exist_ok=True)
        except Exception as e:
            print(e)
            show_error(QMessageBox.Critical, "Ошибка при создании директории исследований", "Директория не может быть создана")
        self.calibration_directory_path = self.calibration_directory.text()
        try:
            os.makedirs(self.calibration_directory_path, exist_ok=True)
        except Exception as e:
            print(e)
            show_error(QMessageBox.Critical, "Ошибка при создании директории калибровок", "Директория не может быть создана")

        self.save_config_file()

    def save_config_file(self):
        config_data = {
            "server_address": self.server_address_input.text(),
            "records_directory_path": self.records_directory_path,
            "calibration_directory_path": self.calibration_directory_path,
            "min_delta_graph_value": self.delta_graph_bounds.min_value.text(),
            "max_delta_graph_value": self.delta_graph_bounds.max_value.text(),
            "min_channels_graph_value": self.channels_graph_bounds.min_value.text(),
            "max_channels_graph_value": self.channels_graph_bounds.max_value.text(),
            "locale": self.locales[self.locale_combobox.currentIndex()],
        }
        json_config_data = json.dumps(config_data, indent=4)
        with open('config.json', 'w') as f:
            f.write(json_config_data)

    def load_configuration(self):
        with open('config.json', 'r') as f:
            config_data = json.loads(f.read())
            self.server_address = config_data["server_address"]
            self.records_directory_path = config_data["records_directory_path"]
            self.calibration_directory_path = config_data["calibration_directory_path"]
            self.min_delta_graph_value = float(config_data["min_delta_graph_value"])
            self.max_delta_graph_value = float(config_data["max_delta_graph_value"])
            self.min_channels_graph_value = float(config_data["min_channels_graph_value"])
            self.max_channels_graph_value = float(config_data["max_channels_graph_value"])
            self.locale = config_data["locale"]

    @staticmethod
    def init_config_file():
        config_data = {
            "server_address": 'localhost:7209',
            "records_directory_path": './records',
            "calibration_directory_path": './calibrationData',
            "min_delta_graph_value": '0',
            "max_delta_graph_value": '30',
            "min_channels_graph_value": '2800',
            "max_channels_graph_value": '3200',
            "locale": 'ru',
        }
        json_config_data = json.dumps(config_data, indent=4)
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as f:
                f.write(json_config_data)

    @staticmethod
    def init_default_directories():
        os.makedirs("./records", exist_ok=True)
        os.makedirs("./calibrationData", exist_ok=True)

    @staticmethod
    def set_min_bound(graph_bounds):
        min_value = graph_bounds.min_value.text()
        is_bound_valid = check_bound(min_value)

        if not is_bound_valid:
            min_value = graph_bounds.previous_min_value
        if float(min_value) >= float(graph_bounds.max_value.text()):
            min_value = graph_bounds.previous_min_value

        graph_bounds.previous_min_value = min_value
        graph_bounds.min_value.setText(str(min_value))

    @staticmethod
    def set_max_bound(graph_bounds):
        max_value = graph_bounds.max_value.text()
        is_bound_valid = check_bound(max_value)

        if not is_bound_valid:
            max_value = graph_bounds.previous_max_value
        if float(max_value) <= float(graph_bounds.min_value.text()):
            max_value = graph_bounds.previous_max_value

        graph_bounds.previous_max_value = max_value
        graph_bounds.max_value.setText(str(max_value))

    def configure_elements(self) -> None:
        self.server_address_input.setText(self.server_address)
        self.records_directory.setText(self.records_directory_path)
        self.calibration_directory.setText(self.calibration_directory_path)
        self.delta_graph_bounds.min_value.setText(str(self.min_delta_graph_value))
        self.delta_graph_bounds.max_value.setText(str(self.max_delta_graph_value))
        self.channels_graph_bounds.min_value.setText(str(self.min_channels_graph_value))
        self.channels_graph_bounds.max_value.setText(str(self.max_channels_graph_value))
        self.records_directory_button.clicked.connect(self.select_records_directory)
        self.records_directory_button.setFixedHeight(BUTTON_HEIGHT)
        self.calibration_directory_button.clicked.connect(self.select_calibration_directory)
        self.calibration_directory_button.setFixedHeight(BUTTON_HEIGHT)
        self.save_button.clicked.connect(self.save)
        self.save_button.setFixedHeight(BUTTON_HEIGHT)
        self.delta_graph_bounds.min_value.textChanged.connect(lambda: self.set_min_bound(self.delta_graph_bounds))
        self.delta_graph_bounds.max_value.textChanged.connect(lambda: self.set_max_bound(self.delta_graph_bounds))
        self.channels_graph_bounds.min_value.textChanged.connect(lambda: self.set_min_bound(self.channels_graph_bounds))
        self.channels_graph_bounds.max_value.textChanged.connect(lambda: self.set_max_bound(self.channels_graph_bounds))
        self.locale_combobox.setFixedHeight(BUTTON_HEIGHT)
        self.locale_combobox.addItem(locales[self.locale]['russian'])
        self.locale_combobox.addItem(locales[self.locale]['english'])
        self.locale_combobox.setCurrentIndex(self.locales.index(self.locale))
