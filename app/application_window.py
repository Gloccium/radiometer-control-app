import base64
import binascii
from PyQt5.QtWidgets import QPushButton, QWidget
from app import message_pb2
from app.graph_widget import PlotCanvas


class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1280
        self.height = 720
        self.left = 100
        self.top = 100
        self.channel_data = []
        self.start()
        self.init_ui()

        # port = "COM3"
        # baudrate = 9600
        # ser = serial.Serial(port, baudrate=baudrate)
        # data = ser.read(1000000)

    def start(self):
        with open('../mocks/mocks_10000_1', "r") as f:
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
        m = PlotCanvas(self, channel_data=self.channel_data)
        m.move(0, 0)
        button = QPushButton('Start', self)
        button.move(500, 0)
        button.resize(140, 100)
        button.clicked.connect(m.plot)
        self.show()