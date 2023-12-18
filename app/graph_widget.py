import base64
import binascii
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSizePolicy
from google.protobuf.message import DecodeError
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import time
from app import message_pb2


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, mocks_data=None, device_controller=None):
        self.x1, self.y1, self.x2, self.y2 = [], [], [], []
        self.first_full = False
        self.second_full = True
        self.is_first_iteration = True

        self.update_rate_ms = 200
        self.current_step_number = 0
        self.max_step_count = 100
        self.current_segment_number = 0
        self.max_segment_count = 5
        self.total_segment_count = 0
        self.time_label = [0]
        self.break_length = 3
        self.offset = 0.2
        self.rescale_sensitivity = 2
        self.last_scaled_y_value = 0

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
        self.time_ms = 0

        self.configure_plot()

    def configure_plot(self):
        self.ax.set_xlim(0, self.max_step_count)
        self.ax.set_xticklabels([f'{round(t, 1)}s' for t in self.time_label])

    def plot(self):
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(self.update_rate_ms)

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

    def update_x_label(self):
        if self.current_step_number % (self.max_step_count // self.max_segment_count) == 0:
            interval = time.time() - self.time_ms
            self.time_ms = time.time()
            self.current_segment_number = (self.current_segment_number + 1) % self.max_segment_count
            current_time = self.time_label[self.current_segment_number - 1] + interval
            if self.total_segment_count < self.max_segment_count - 1:
                self.time_label.append(current_time)
            else:
                self.time_label[self.current_segment_number] = current_time
            self.ax.set_xticklabels([f'{round(tm, 1)}s' for tm in self.time_label])
            self.total_segment_count += 1

    def plot_data(self):
        if self.first_full:
            self.x1 = self.x1[1:len(self.x1)]
            self.y1 = self.y1[1:len(self.y1)]

        if self.second_full:
            self.x2 = self.x2[1:len(self.x2)]
            self.y2 = self.y2[1:len(self.y2)]

        if not self.first_full:
            self.lines.set_xdata(self.x1 + [None] * self.break_length + self.x2[self.break_length:])
            self.lines.set_ydata(self.y1 + [None] * self.break_length + self.y2[self.break_length:])

        if not self.second_full:
            self.lines.set_xdata(self.x2 + [None] * self.break_length + self.x1[self.break_length:])
            self.lines.set_ydata(self.y2 + [None] * self.break_length + self.y1[self.break_length:])

        points1 = self.ax.plot(self.x1, self.y1, 'b')
        points2 = self.ax.plot(self.x2, self.x2, 'b')

        for p1, p2 in zip(points1, points2):
            p1.remove()
            p2.remove()

    def add_points(self, current_value):
        if not self.first_full:
            self.x1.append(self.current_step_number)
            self.y1.append(current_value)

        if not self.second_full:
            self.x2.append(self.current_step_number)
            self.y2.append(current_value)

    def check_iteration(self):
        if self.is_first_iteration:
            self.time_ms = time.time()
            self.ax.set_ylim(self.y1[0] - self.offset, self.y1[0] + self.offset)
            self.last_scaled_y_value = self.y1[0]
            self.is_first_iteration = False

    def rescale(self):
        if not self.first_full and (self.y1[-1] > self.last_scaled_y_value + self.offset / self.rescale_sensitivity
                                    or self.y1[-1] < self.last_scaled_y_value - self.offset / self.rescale_sensitivity):
            self.last_scaled_y_value = self.y1[-1]
            self.ax.set_ylim(self.y1[-1] - self.offset, self.y1[-1] + self.offset)

        if not self.second_full and (self.y2[-1] > self.last_scaled_y_value + self.offset / self.rescale_sensitivity
                                     or self.y2[
                                         -1] < self.last_scaled_y_value - self.offset / self.rescale_sensitivity):
            self.last_scaled_y_value = self.y2[-1]
            self.ax.set_ylim(self.y2[-1] - self.offset, self.y2[-1] + self.offset)

    def switch_plots(self):
        if self.current_step_number % self.max_step_count == 0:
            self.current_step_number = 0
            self.first_full, self.second_full = self.second_full, self.first_full
            if self.first_full:
                self.ax.set_ylim(self.y1[-1] - self.offset, self.y1[-1] + self.offset)
            if self.second_full:
                self.ax.set_ylim(self.y2[-1] - self.offset, self.y2[-1] + self.offset)

    def get_current_value(self):
        current_value = 0

        if self.mode == 'MOCKS':
            if self.previous_value == 0:
                current_value = sum(self.mocks_data[self.current_step_number]) / len(
                    (self.mocks_data[self.current_step_number]))
            else:
                current_value = self.previous_value * self.previous_modifier \
                                + sum(self.mocks_data[self.current_step_number]) / len(
                    (self.mocks_data[self.current_step_number])) * self.current_modifier
        if self.mode == 'DEVICE':
            self.get_packages()
            if not self.channel_data:
                return
            if self.previous_value == 0:
                current_value = sum([sum(x) / len(x) for x in self.channel_data]) / len(self.channel_data)
            else:
                current_value = self.previous_value * self.previous_modifier \
                                + sum([sum(x) / len(x) for x in self.channel_data]) / len(
                    self.channel_data) * self.current_modifier

        return current_value

    def update_figure(self):
        current_value = self.get_current_value()

        self.previous_value = current_value
        self.current_step_number += 1

        self.add_points(current_value)
        self.check_iteration()
        self.rescale()
        self.switch_plots()
        self.plot_data()

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.update_x_label()
