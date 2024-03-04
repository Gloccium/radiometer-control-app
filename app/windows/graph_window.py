import asyncio
import json
from datetime import datetime

import aiohttp
import serial.tools.list_ports
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QLineEdit, \
    QCheckBox
from qasync import asyncSlot, asyncClose
from serial import Serial, SerialException

from app.const import BUTTON_HEIGHT
from app.utils.calibration_validation import validate_calibration
from app.utils.error_messages import show_error, is_network_error
from app.threads.device_controller import DeviceController
from app.threads.timer import Timer
from app.widgets.layouts.square_layout import SquareLayout
from app.widgets.graph_widget.graph_widget import GraphWidget
from app.widgets.list_adapter_widget.single_list_adapter_widget import SingleListAdapter
from app.widgets.bounds.graph_bounds import GraphBounds
from app.windows.calibration_window import CalibrationWindow
from app.windows.device_selection_window import DeviceSelectionWindow
from app.windows.device_window import DeviceWindow


class GraphWindow(QWidget):
    def __init__(self, settings_window):
        super().__init__()
        self.session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
        self.settings_window = settings_window
        self.sending_window = None

        self.plot = None
        self.start_button = QPushButton('Начать исследование', self)
        self.toggle_channels_button = QPushButton('Скрыть каналы', self)
        self.finish_button = QPushButton('Закончить исследование', self)
        self.data = []
        self.record_filename = None

        self.port_list = QListWidget()
        self.update_port_list_button = QPushButton('Обновить список портов', self)
        self.selected_port = None
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]

        self.controls = SquareLayout(self.toggle_channels_button, self.update_port_list_button,
                                     self.start_button, self.finish_button)

        self.delta_graph_auto_mode = QCheckBox("Показывать весь график температуры")
        self.delta_graph_bounds = GraphBounds('Min графика температуры', 'Max графика температуры')

        self.channels_graph_auto_mode = QCheckBox("Показывать весь график каналов")
        self.channels_graph_bounds = GraphBounds('Min графика каналов', 'Max графика каналов')

        self.bounds_controls = SquareLayout(self.delta_graph_auto_mode, self.channels_graph_auto_mode,
                                            self.delta_graph_bounds, self.channels_graph_bounds)

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
            "Select a File",
            self.settings_window.calibration_directory_path
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
        devices_url = f'https://{self.settings_window.server_address}/devices'
        headers = {"Authorization": f'Bearer {self.sending_window.token}'}
        try:
            async with self.session.get(devices_url, headers=headers, timeout=3) as r:
                if is_network_error(r.status):
                    return
                data = await r.read()
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка соединения", "Не удалось установить соединение с сервером")
            print(e)
            return

        self.devices = json.loads(data)

    @asyncSlot()
    async def update_calibrations(self):
        calibrations_url = f'https://{self.settings_window.server_address}/calibrations'
        headers = {"Authorization": f'Bearer {self.sending_window.token}'}
        try:
            async with self.session.get(calibrations_url, headers=headers, timeout=3) as r:
                if is_network_error(r.status):
                    return
                data = await r.read()
        except Exception as e:
            show_error(QMessageBox.Critical, "Ошибка соединения", "Не удалось установить соединение с сервером")
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
        now = datetime.now()
        self.record_filename = f'Record {now.strftime("%d-%m-%Y %H-%M")}'
        with open(f'{self.settings_window.records_directory_path}/{self.record_filename}', 'wb') as f:
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

    def toggle_delta_graph_auto_mode(self):
        if self.delta_graph_auto_mode.isChecked():
            self.plot.delta_graph_auto_mode = True
            self.delta_graph_bounds.setDisabled(True)
        else:
            self.plot.delta_graph_auto_mode = False
            self.plot.rescale_delta_graph_manually()
            self.delta_graph_bounds.setDisabled(False)

    def toggle_channels_graph_auto_mode(self):
        if self.channels_graph_auto_mode.isChecked():
            self.plot.channels_graph_auto_mode = True
            self.channels_graph_bounds.setDisabled(True)
        else:
            self.plot.channels_graph_auto_mode = False
            self.plot.rescale_channels_graph_manually()
            self.channels_graph_bounds.setDisabled(False)

    def rescale_delta_graph(self):
        min_value = self.delta_graph_bounds.min_value.text().lstrip('0')
        max_value = self.delta_graph_bounds.max_value.text().lstrip('0')
        if self.delta_graph_bounds.min_value.text() == '' or self.delta_graph_bounds.max_value.text() == '':
            self.delta_graph_bounds.min_value.setText('1')
            self.delta_graph_bounds.max_value.setText('1')
        else:
            self.delta_graph_bounds.min_value.setText(min_value)
            self.delta_graph_bounds.max_value.setText(max_value)
        self.plot.delta_graph.min = float(self.delta_graph_bounds.min_value.text())
        self.plot.delta_graph.max = float(self.delta_graph_bounds.max_value.text())
        self.plot.rescale_delta_graph_manually()

    def rescale_channels_graph(self):
        min_value = self.channels_graph_bounds.min_value.text().lstrip('0')
        max_value = self.channels_graph_bounds.max_value.text().lstrip('0')
        if self.channels_graph_bounds.min_value.text() == '' or self.channels_graph_bounds.max_value.text() == '':
            self.channels_graph_bounds.min_value.setText('1')
            self.channels_graph_bounds.max_value.setText('1')
        else:
            self.channels_graph_bounds.min_value.setText(min_value)
            self.channels_graph_bounds.max_value.setText(max_value)
        self.plot.channels_graph.min = float(self.channels_graph_bounds.min_value.text())
        self.plot.channels_graph.max = float(self.channels_graph_bounds.max_value.text())
        self.plot.rescale_channels_graph_manually()

    def configure_elements(self) -> None:
        self.start_button.clicked.connect(self.start_device)
        self.start_button.setFixedHeight(BUTTON_HEIGHT)

        self.toggle_channels_button.clicked.connect(self.toggle_channels)
        self.toggle_channels_button.setFixedHeight(BUTTON_HEIGHT)

        self.finish_button.clicked.connect(self.finish)
        self.finish_button.setDisabled(True)
        self.finish_button.setFixedHeight(BUTTON_HEIGHT)

        self.update_port_list_button.clicked.connect(self.update_port_list)
        self.update_port_list_button.setFixedHeight(BUTTON_HEIGHT)

        self.port_list.setFixedHeight(120)
        self.port_list.clicked.connect(self.select_port)

        self.add_device_button.clicked.connect(self.add_device)
        self.add_device_button.setFixedHeight(BUTTON_HEIGHT)

        self.add_calibration_button.clicked.connect(self.add_calibration)
        self.add_calibration_button.setFixedHeight(BUTTON_HEIGHT)

        self.select_device_button.clicked.connect(self.select_device)
        self.select_device_button.setFixedHeight(BUTTON_HEIGHT)

        self.filename.setDisabled(True)
        self.select_local_calibration_button.clicked.connect(self.select_local_calibration)
        self.select_local_calibration_button.setFixedHeight(BUTTON_HEIGHT)

        self.delta_graph_bounds.min_value.setText(str(self.settings_window.min_delta_graph_value))
        self.delta_graph_bounds.max_value.setText(str(self.settings_window.max_delta_graph_value))
        self.channels_graph_bounds.min_value.setText(str(self.settings_window.min_channels_graph_value))
        self.channels_graph_bounds.max_value.setText(str(self.settings_window.max_channels_graph_value))

        self.delta_graph_auto_mode.stateChanged.connect(self.toggle_delta_graph_auto_mode)
        self.delta_graph_bounds.min_value.textChanged.connect(self.rescale_delta_graph)
        self.delta_graph_bounds.max_value.textChanged.connect(self.rescale_delta_graph)

        self.channels_graph_auto_mode.stateChanged.connect(self.toggle_channels_graph_auto_mode)
        self.channels_graph_bounds.min_value.textChanged.connect(self.rescale_channels_graph)
        self.channels_graph_bounds.max_value.textChanged.connect(self.rescale_channels_graph)

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
