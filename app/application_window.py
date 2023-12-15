import base64
import binascii
import serial.tools.list_ports
from PyQt5.QtWidgets import QPushButton, QWidget
from app import message_pb2
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

        self.local_channel_data = []
        self.get_data()

        # self.device_thread = QThread()
        # self.device_controller = DeviceController()
        # self.device_controller.moveToThread(self.device_thread)
        # self.device_thread.started.connect(self.device_controller.load_data)
        # self.device_thread.start()

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
                test = message_pb2.Message()
                test.ParseFromString(data)
                self.local_channel_data.append(test.allData.channelData)

    def init_plot(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.plot = PlotCanvas(self, channel_data=self.local_channel_data)
        self.plot.move(0, 0)

    def init_control_buttons(self):
        start_button = QPushButton('Start', self)
        start_button.move(100, 1000)
        start_button.resize(140, 100)
        start_button.clicked.connect(self.plot.plot)

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
