import asyncio
import json

import aiohttp
import serial.tools.list_ports
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QLineEdit
from qasync import asyncSlot, asyncClose
from serial import Serial, SerialException

from app.utils.calibration_validation import validate_calibration
from app.utils.error_message import show_error
from app.threads.device_controller import DeviceController
from app.threads.timer import Timer
from app.widgets.graph_widget.graph_widget import GraphWidget
from app.widgets.list_adapter_widget.single_list_adapter_widget import SingleListAdapter
from app.windows.calibration_window import CalibrationWindow
from app.windows.device_selection_window import DeviceSelectionWindow
from app.windows.device_window import DeviceWindow


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = None
        self.sending_window = None

        self.plot = None
        self.start_button = None
        self.toggle_channels_button = None
        self.finish_button = None
        self.data = []

        self.port_list = QListWidget()
        self.update_port_list_button = None
        self.selected_port = None
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]

        self.devices = []
        self.device_window = None
        self.selected_device = None
        self.add_device_button = QPushButton('Добавить устройство', self)

        self.calibrations = []
        self.calibration_window = None
        self.selected_calibration = None
        self.calibration_data = None
        self.add_calibration_button = QPushButton('Добавить калибровку', self)

        self.device_selection_window = None
        self.select_device_button = QPushButton('Выбрать устройство и калибровку', self)

        self.filename = QLineEdit(self)
        self.select_local_calibration_button = QPushButton('Выбрать калибровку с устройства', self)

        self.device_thread = QThread()
        self.device_controller = DeviceController()
        self.device_controller.moveToThread(self.device_thread)
        self.device_thread.started.connect(self.device_controller.run)

        self.init_plot()

        self.timer_thread = QThread()
        self.timer = Timer(self.plot)
        self.timer.moveToThread(self.timer_thread)
        self.timer_thread.started.connect(self.timer.start)

        self.configure_elements()
        self.update_port_list()
        self.set_visibility()

    def init_plot(self) -> None:
        self.plot = GraphWidget(self, device_controller=self.device_controller)
        self.plot.move(0, 0)

    def update_port_list(self):
        self.selected_port = None
        self.port_list.clear()
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]
        for port in self.active_ports:
            list_adapter = SingleListAdapter()
            list_adapter.set_name(port)

            list_adapter_item = QListWidgetItem()
            list_adapter_item.setSizeHint(list_adapter.sizeHint())
            self.port_list.addItem(list_adapter_item)
            self.port_list.setItemWidget(list_adapter_item, list_adapter)

    def select_port(self):
        self.selected_port = self.port_list.currentRow()
        self.device_controller.port = self.active_ports[self.selected_port]

    def add_device(self):
        self.device_window = DeviceWindow(self, self.settings_window, self.sending_window)
        self.device_window.show()

    def add_calibration(self):
        self.calibration_window = CalibrationWindow(self, self.settings_window, self.sending_window)
        self.calibration_window.show()

    def select_device(self):
        self.device_selection_window = DeviceSelectionWindow(self, self.settings_window, self.sending_window)
        self.device_selection_window.show()

    def select_local_calibration(self):
        filename, ok = QFileDialog.getOpenFileName(
            self,
            "Select a File"
        )
        if filename != '':
            with open(filename, 'r', encoding='utf-8') as f:
                data = f.read()
                if validate_calibration(data):
                    self.filename.setText(filename)
                    self.calibration_data = json.loads(data)
                else:
                    self.filename.setText('')
                    self.calibration_data = None

    @asyncSlot()
    async def update_devices(self):
        devices_url = f'https://{self.settings_window.server_address.text()}/devices'
        devices_url = "https://localhost:7209/devices"
        headers = {'Token': self.sending_window.token}
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

    @asyncSlot()
    async def update_calibrations(self):
        calibrations_url = f'https://{self.settings_window.server_address.text()}/calibrations'
        calibrations_url = "https://localhost:7209/calibrations"
        headers = {'Token': self.sending_window.token}
        try:
            async with self.session.get(calibrations_url, headers=headers, timeout=3) as r:
                if r.status != 200:
                    print(r.status)
                    show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
                    return
                data = await r.read()
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка сети", "Неизвестная ошибка сети")
            print(e)
            return

        self.calibrations = json.loads(data)

    @asyncClose
    async def closeEvent(self, event):
        await self.session.close()

    def start_device(self) -> None:
        if self.calibration_data is None or self.selected_port is None:
            show_error(QMessageBox.Warning, "Ошибка запуска", "Необходимо выбрать калибровку и порт")
            return
        try:
            serial = Serial(self.device_controller.port, baudrate=self.device_controller.baudrate)
            serial.reset_input_buffer()
            serial.close()
        except SerialException:
            show_error(QMessageBox.Critical, "Ошибка подключения", "Невозможно подключиться к выбранному порту")
            print('Could not open port')
            return
        self.plot.calibration_data = self.calibration_data["calibrationData"]
        self.plot.delta_ax.set_ylabel(self.calibration_data["yLabel"])
        self.device_thread.start()
        self.timer_thread.start()
        self.finish_button.setDisabled(False)
        self.start_button.setDisabled(True)

    def write_data(self):
        with open('../data', 'wb') as f:
            [f.write(s) for s in self.data]

    def finish(self):
        self.timer.stop()
        self.timer_thread.quit()
        self.device_thread.quit()
        self.write_data()
        self.data = []
        self.start_button.setDisabled(False)
        self.finish_button.setDisabled(True)
        self.plot.reinitialize_plot()
        self.device_controller.stop()

    def toggle_channels(self):
        self.plot.toggle_channels()
        if self.plot.is_channels_visible:
            self.toggle_channels_button.setText('Скрыть каналы')
        else:
            self.toggle_channels_button.setText('Показать каналы')

    def configure_elements(self) -> None:
        self.start_button = QPushButton('Начать исследование', self)
        self.start_button.clicked.connect(self.start_device)

        self.toggle_channels_button = QPushButton('Скрыть каналы', self)
        self.toggle_channels_button.clicked.connect(self.toggle_channels)

        self.finish_button = QPushButton('Закончить исследование', self)
        self.finish_button.clicked.connect(self.finish)
        self.finish_button.setDisabled(True)

        self.update_port_list_button = QPushButton('Обновить список портов', self)
        self.update_port_list_button.clicked.connect(self.update_port_list)

        self.port_list.setFixedHeight(120)
        self.port_list.clicked.connect(self.select_port)

        self.add_device_button.clicked.connect(self.add_device)
        self.add_calibration_button.clicked.connect(self.add_calibration)
        self.select_device_button.clicked.connect(self.select_device)

        self.filename.setDisabled(True)
        self.select_local_calibration_button.clicked.connect(self.select_local_calibration)

    def set_visibility(self):
        if self.sending_window is not None and self.sending_window.is_authentificated:
            self.add_device_button.show()
            self.add_calibration_button.show()
            self.select_device_button.show()
            self.filename.hide()
            self.select_local_calibration_button.hide()
        else:
            self.add_device_button.hide()
            self.add_calibration_button.hide()
            self.select_device_button.hide()
            self.filename.show()
            self.select_local_calibration_button.show()
