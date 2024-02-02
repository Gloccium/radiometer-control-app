import serial.tools.list_ports
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QListWidgetItem, QMessageBox
from serial import Serial, SerialException

from app.utils.error_message import show_error
from app.threads.device_controller import DeviceController
from app.threads.timer import Timer
from app.widgets.graph_widget.graph_widget import GraphWidget
from app.widgets.list_adapter_widget.single_list_adapter_widget import SingleListAdapter


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.plot = None
        self.start_button = None
        self.toggle_channels_button = None
        self.finish_button = None
        self.data = []

        self.port_list = QListWidget()
        self.update_port_list_button = None
        self.selected_port = None
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]

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

    def start_device(self) -> None:
        if self.selected_port == None:
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
            self.toggle_channels_button.setText('Hide channels')
        else:
            self.toggle_channels_button.setText('Show channels')

    def configure_elements(self) -> None:
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_device)

        self.toggle_channels_button = QPushButton('Hide channels', self)
        self.toggle_channels_button.clicked.connect(self.toggle_channels)

        self.finish_button = QPushButton('Finish', self)
        self.finish_button.clicked.connect(self.finish)
        self.finish_button.setDisabled(True)

        self.update_port_list_button = QPushButton('Update port list', self)
        self.update_port_list_button.clicked.connect(self.update_port_list)

        self.port_list.setFixedHeight(120)
        self.port_list.clicked.connect(self.select_port)
