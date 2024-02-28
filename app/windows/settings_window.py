import json
import os

from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QFileDialog, QMessageBox, QLabel

from app.utils.error_messages import show_error
from app.widgets.offset_parameter_widget.offset_parameter_widget import OffsetParameter


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.records_directory_path = ''
        self.calibration_directory_path = ''
        self.delta_graph_offset_value = None
        self.channels_graph_offset_value = None
        self.server_address_label = QLabel('Адрес сервера')
        self.server_address = 'localhost:7209'
        self.server_address_input = QLineEdit(self)
        self.records_directory = QLineEdit(self)
        self.records_directory_button = QPushButton('Выбрать директорию для исследований', self)
        self.calibration_directory = QLineEdit(self)
        self.calibration_directory_button = QPushButton('Выбрать директорию для калибровок', self)
        self.delta_graph_offset = OffsetParameter('Окно по оси Y графика температуры')
        self.channels_graph_offset = OffsetParameter('Окно по оси Y графика каналов')
        self.save_button = QPushButton('Сохранить', self)
        self.init_config_file()
        self.init_default_directories()
        self.load_configuration()
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

        if self.delta_graph_offset.offset_value.text() == '' or self.channels_graph_offset.offset_value.text() == '':
            show_error(QMessageBox.Critical, "Ошибка при сохранении параметров графиков", "Параметры графиков не могут быть пустыми")
            return

        self.save_config_file()

    def save_config_file(self):
        config_data = {
            "records_directory_path": self.records_directory_path,
            "calibration_directory_path": self.calibration_directory_path,
            "delta_graph_offset_value": self.delta_graph_offset.offset_value.text(),
            "channels_graph_offset_value": self.channels_graph_offset.offset_value.text(),
        }
        json_config_data = json.dumps(config_data)
        with open('config.json', 'w') as f:
            f.write(json_config_data)

    def load_configuration(self):
        with open('config.json', 'r') as f:
            config_data = json.loads(f.read())
            self.records_directory_path = config_data["records_directory_path"]
            self.calibration_directory_path = config_data["calibration_directory_path"]
            self.delta_graph_offset_value = int(config_data["delta_graph_offset_value"])
            self.channels_graph_offset_value = int(config_data["channels_graph_offset_value"])

    @staticmethod
    def init_config_file():
        config_data = {
            "records_directory_path": './records',
            "calibration_directory_path": './calibrationData',
            "delta_graph_offset_value": '2',
            "channels_graph_offset_value": '500',
        }
        json_config_data = json.dumps(config_data)
        if not os.path.exists('config.json'):
            with open('config.json', 'w') as f:
                f.write(json_config_data)

    @staticmethod
    def init_default_directories():
        os.makedirs("./records", exist_ok=True)
        os.makedirs("./calibrationData", exist_ok=True)

    def configure_elements(self) -> None:
        self.server_address_input.setText(self.server_address)
        self.records_directory.setText(self.records_directory_path)
        self.calibration_directory.setText(self.calibration_directory_path)
        self.delta_graph_offset.offset_value.setText(str(self.delta_graph_offset_value))
        self.channels_graph_offset.offset_value.setText(str(self.channels_graph_offset_value))
        self.records_directory_button.clicked.connect(self.select_records_directory)
        self.calibration_directory_button.clicked.connect(self.select_calibration_directory)
        self.save_button.clicked.connect(self.save)
