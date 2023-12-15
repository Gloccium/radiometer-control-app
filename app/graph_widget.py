import base64
import binascii
import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSizePolicy
from google.protobuf.message import DecodeError
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from app import message_pb2


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, mocks_data=None, device_controller=None):
        self.x = []
        self.y = []
        self.count = 0
        self.plot_range = 100
        self.update_rate = 200
        self.previous_modifier = 0.999
        self.current_modifier = 0.001

        self.mode = 'DEVICE'

        self.mocks_data = mocks_data

        self.device_controller = device_controller
        self.channel_data = []
        self.last_package = 0

        self.previous_value = 0
        self.error_count = 0
        self.package_count = 0

        self.figure, self.ax = plt.subplots(figsize=(16, 9))
        self.lines, = self.ax.plot([], [], 'b')

        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.setParent(parent)
        self.timer = QTimer()

        self.configure_plot()

    def configure_plot(self):
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(0, self.plot_range)

    def plot(self):
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(self.update_rate)

    def stop_plot(self):
        self.timer.stop()

    def get_packages(self):
        self.channel_data = []
        length = len(self.device_controller.channel_data)
        channel_data = self.device_controller.channel_data[self.last_package:length]
        self.last_package = length
        self.decode_packages(channel_data)

    def decode_packages(self, channel_data):
        for packet in channel_data:
            self.package_count += 1
            try:
                data = base64.b64decode(packet)
            except binascii.Error:
                print('Invalid packet')
                continue
            try:
                message = message_pb2.Message()
                message.ParseFromString(data)
                if message.allData.channelData:
                    self.channel_data.append(message.allData.channelData)
            except DecodeError:
                print('Invalid packet')
                self.error_count += 1
                continue

    def update_figure(self):
        current_value = 0

        if self.mode == 'MOCKS':
            if self.previous_value == 0:
                current_value = sum(self.mocks_data[self.count]) / len((self.mocks_data[self.count]))
            else:
                current_value = self.previous_value * self.previous_modifier \
                                + sum(self.mocks_data[self.count]) / len((self.mocks_data[self.count])) * self.current_modifier
        if self.mode == 'DEVICE':
            self.get_packages()
            if not self.channel_data:
                return
            if self.previous_value == 0:
                current_value = sum([sum(x) / len(x) for x in self.channel_data]) / len(self.channel_data)
            else:
                current_value = self.previous_value * self.previous_modifier \
                                + sum([sum(x) / len(x) for x in self.channel_data]) / len(self.channel_data) * self.current_modifier

        self.x.append(self.count)
        self.y.append(current_value)
        self.previous_value = current_value
        self.count += 1
        if self.count > self.plot_range:
            self.ax.set_xlim(self.count - self.plot_range, self.count)
        self.lines.set_xdata(self.x)
        self.lines.set_ydata(self.y)
        self.figure.canvas.draw()
        self.ax.plot(self.x, self.y, 'b')
        self.figure.canvas.flush_events()
