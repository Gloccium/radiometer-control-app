import base64
import binascii

import serial.tools.list_ports
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QPushButton, QWidget

from app import message_pb2
from app.device_controller import DeviceController
from app.graph_widget import PlotCanvas


class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1600
        self.height = 1200
        self.left = 100
        self.top = 100

        self.selected_port = ''
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]
        self.port_buttons = [QPushButton(f'COM{i}', self) for i in range(1, 17)]
        self.plot = None

        self.mocks_data = []
        self.get_data()

        self.device_thread = QThread()
        self.device_controller = DeviceController()
        self.device_controller.moveToThread(self.device_thread)
        self.device_thread.started.connect(self.device_controller.load_data)

        self.init_plot()
        self.init_control_buttons()
        self.configure_port_buttons()
        self.show()

        # port = "COM3"
        # baudrate = 9600
        # ser = serial.Serial(port, baudrate=baudrate)
        # data = ser.read(1000000)

        # print()
        # port = "COM2"
        # baudrate = 9600
        # ser = serial.Serial(port, baudrate=baudrate)
        # data = ser.read(1000)
        # print(data)

    def get_data(self):
        with open('../mocks/mocks_200000_1', "r") as f:
            packets = f.readlines()
            for packet in packets:
                try:
                    data = base64.b64decode(packet)
                except binascii.Error:
                    print('Invalid packet')
                    continue
                message = message_pb2.Message()
                message.ParseFromString(data)
                self.mocks_data.append(message.allData.channelData)

    def init_plot(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.plot = PlotCanvas(self, mocks_data=self.mocks_data, device_controller=self.device_controller)
        self.plot.move(0, 0)

    def start_mocks(self):
        self.plot.mode = 'MOCKS'
        self.plot.plot()

    def start_device(self):
        self.plot.mode = 'DEVICE'
        self.device_thread.start()
        if self.device_controller.port_error:
            print('Could not open port')
            self.device_thread.quit()
        self.plot.plot()

    def init_control_buttons(self):
        start_mocks_button = QPushButton('Start mocks', self)
        start_mocks_button.move(100, 1000)
        start_mocks_button.resize(140, 60)
        start_mocks_button.clicked.connect(self.start_mocks)

        start_device_button = QPushButton('Start device', self)
        start_device_button.move(100, 1100)
        start_device_button.resize(140, 60)
        start_device_button.clicked.connect(self.start_device)

        stop_button = QPushButton('Stop', self)
        stop_button.move(300, 1000)
        stop_button.resize(140, 100)
        stop_button.clicked.connect(self.plot.stop_plot)

        update_port_button = QPushButton('Update ports list', self)
        update_port_button.move(500, 1000)
        update_port_button.resize(140, 100)
        update_port_button.clicked.connect(self.update_ports)

    def update_ports(self):
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]
        self.configure_port_buttons()

    def select_port(self, port):
        self.selected_port = port
        self.device_controller.port = self.selected_port
        self.configure_port_buttons()

    def configure_port_buttons(self):
        offset = 1000
        for i in range(len(self.port_buttons)):
            if self.port_buttons[i].text() in self.active_ports:
                self.port_buttons[i].move(700, offset)
                self.port_buttons[i].resize(100, 40)
                self.port_buttons[i].disconnect()
                self.port_buttons[i].clicked.connect(lambda x, i=i: self.select_port(self.active_ports[i]))
                self.port_buttons[i].setStyleSheet(f'QPushButton {{background-color: '
                                                   f'{ "#008000" if self.port_buttons[i].text() == self.selected_port else "#FFFFFF"} }}')
                offset += 60
                self.port_buttons[i].show()
            else:
                self.port_buttons[i].hide()
