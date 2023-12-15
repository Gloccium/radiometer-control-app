import base64
import binascii
from PyQt5.QtWidgets import QPushButton, QWidget
from app import message_pb2
from app.graph_widget import PlotCanvas
import serial.tools.list_ports


class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1600
        self.height = 1200
        self.left = 100
        self.top = 100
        self.channel_data = []
        self.get_data()
        self.init_ui()

        # print(list(serial.tools.list_ports.comports()))

        # port = "COM3"
        # baudrate = 9600
        # ser = serial.Serial(port, baudrate=baudrate)
        # data = ser.read(1000000)

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
                self.channel_data.append(test.allData.channelData)

    def init_ui(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        plot = PlotCanvas(self, channel_data=self.channel_data)
        plot.move(0, 0)

        start_button = QPushButton('Start', self)
        start_button.move(100, 1000)
        start_button.resize(140, 100)
        start_button.clicked.connect(plot.plot)

        stop_button = QPushButton('Stop', self)
        stop_button.move(300, 1000)
        stop_button.resize(140, 100)
        stop_button.clicked.connect(plot.stop_plot)

        self.show()
