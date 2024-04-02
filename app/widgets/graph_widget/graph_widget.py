import base64
import binascii
import json
import time
from queue import Queue

import scipy
from PyQt5.QtWidgets import QSizePolicy
from google.protobuf.message import DecodeError
from matplotlib import pyplot as plt, gridspec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import signal

from app.widgets.graph_widget.graph_data import GraphData
from app.messages import message_pb2
from app.signals.my_signal import MySignal
from app.locales.locales import locales


class GraphWidget(FigureCanvas):
    def __init__(self, graph_window=None, device_controller=None):
        self.graph_window = graph_window
        self.current_step_number = 0
        self.max_step_count = 2000
        self.current_segment_number = 0
        self.max_segment_count = 8
        self.total_segment_count = 0
        self.time_label = [0.0]
        self.break_length = 10
        self.calibration_data = []

        self.device_controller = device_controller
        self.channel_data = []
        self.channel_window = 1000
        self.channel_a = []
        self.channel_b = []

        self.b1_param, self.a1_param = signal.iirfilter(2, 10, ftype='butter', btype='lowpass', fs=12000)
        self.b2_param, self.a2_param = signal.iirfilter(2, 0.1, ftype='butter', btype='lowpass', fs=400)
        self.decimation_rate = 10

        self.segment_signals_count = 0
        self.previous_value = 0
        self.error_count = 0
        self.package_count = 0

        self.last_signals = []
        self.last_signals_range = 100
        self.last_signals_time_interval = 5

        self.is_channels_visible = True
        self.figure = plt.figure(figsize=(21, 7))
        self.double_gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])
        self.single_gs = gridspec.GridSpec(2, 1, height_ratios=[1000, 1])
        self.delta_ax = self.figure.add_subplot(self.double_gs[0])
        self.channels_ax = self.figure.add_subplot(self.double_gs[1])
        self.delta_ax.grid()
        self.channels_ax.grid()
        plt.subplots_adjust(left=0.03, right=0.98)
        self.delta_lines, = self.delta_ax.plot([], [], 'r')
        self.channel_a_lines, = self.channels_ax.plot([], [], 'g')
        self.channel_b_lines, = self.channels_ax.plot([], [], 'b')
        self.channels_ax.legend(loc="upper right")
        self.set_texts()

        self.delta_graph_auto_mode = False
        self.channels_graph_auto_mode = False
        self.delta_graph = GraphData(self.delta_ax, self.graph_window.settings_window.min_delta_graph_value,
                                     self.graph_window.settings_window.max_delta_graph_value, self.delta_lines, None)
        self.channels_graph = GraphData(self.channels_ax, self.graph_window.settings_window.min_channels_graph_value,
                                        self.graph_window.settings_window.max_channels_graph_value, self.channel_a_lines,
                                        self.channel_b_lines)
        self.graphs = [self.delta_graph, self.channels_graph]

        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.setParent(graph_window)

        self.signal = MySignal()
        self.signal.sig_no_args.connect(self.update_figure)

        self.q1 = Queue()
        with open(r'C:\Users\aburg\Desktop\radiometer-control-app\app\records\Record 01-04-2024 12-31 egor') as f:
            data = f.readlines()
            [self.q1.put(d) for d in data]

        self.result1 = []

        self.q2 = Queue()
        with open(r'C:\Users\aburg\Desktop\radiometer-control-app\app\records\Record 01-04-2024 12-31 egor') as f:
            data = f.readlines()
            [self.q2.put(d) for d in data]

        self.result2 = []

        self.time_ms = 0
        self.configure_plot()

    def set_texts(self):
        self.delta_ax.set_title(locales[self.graph_window.settings_window.locale]['temperature'])
        self.channels_ax.set_title(locales[self.graph_window.settings_window.locale]['channels'])
        self.channels_ax.legend(labels=[locales[self.graph_window.settings_window.locale]['channel_a'],
                                        locales[self.graph_window.settings_window.locale]['channel_b']])
        plt.draw()

    def reinitialize_plot(self):
        self.delta_ax.clear()
        self.channels_ax.clear()

        self.channel_data = []
        self.channel_a = []
        self.channel_b = []
        self.current_step_number = 0
        self.current_segment_number = 0
        self.total_segment_count = 0
        self.time_label = [0.0]

        self.delta_lines, = self.delta_ax.plot([], [], 'r')
        self.channel_a_lines, = self.channels_ax.plot([], [], 'g')
        self.channel_b_lines, = self.channels_ax.plot([], [], 'b')

        self.delta_ax.grid()
        self.channels_ax.grid()

        self.delta_graph = GraphData(self.delta_ax, self.delta_graph.min, self.delta_graph.max,
                                     self.delta_lines, None)
        self.channels_graph = GraphData(self.channels_ax, self.channels_graph.min, self.channels_graph.max,
                                        self.channel_a_lines, self.channel_b_lines)
        self.graphs = [self.delta_graph, self.channels_graph]

        self.set_texts()
        self.configure_plot()

    def toggle_channels(self):
        self.is_channels_visible = not self.is_channels_visible
        self.channels_ax.set_visible(self.is_channels_visible)
        if self.is_channels_visible:
            self.delta_ax.set_position(self.double_gs[0].get_position(self.figure))
            self.channels_ax.set_position(self.double_gs[1].get_position(self.figure))
        else:
            self.delta_ax.set_position(self.single_gs[0].get_position(self.figure))
            self.channels_ax.set_position(self.single_gs[1].get_position(self.figure))
        plt.draw()

    def configure_plot(self) -> None:
        for graph in self.graphs:
            graph.ax.set_xlim(0, self.max_step_count)
            graph.ax.set_xticklabels([f'{round(t, 1)}s' for t in self.time_label])

    def decode_packages(self, channel_data: list[str]) -> None:
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
                if message.allData:
                    self.channel_data.append(message.allData)
            except DecodeError:
                print('Invalid packet')
                self.error_count += 1
                continue

    def update_status_bar(self) -> None:
        count = 0
        last_signal_time = self.last_signals[-1][1]
        for sig in reversed(self.last_signals):
            if sig[1] > last_signal_time - self.last_signals_time_interval:
                count += sig[0]
            else:
                break
        self.graph_window.status_bar.showMessage(f'{locales[self.graph_window.settings_window.locale]["signals_per"]} '
                                                 f'{self.last_signals_time_interval}'
                                                 f'{locales[self.graph_window.settings_window.locale]["sec"]}: {count}')

    def update_x_label(self) -> None:
        if self.current_step_number % (self.max_step_count // self.max_segment_count) == 0:
            interval = self.segment_signals_count / self.device_controller.device_frequency
            self.current_segment_number = (self.current_segment_number + 1) % self.max_segment_count
            current_time = self.time_label[self.current_segment_number - 1] + interval
            if self.total_segment_count < self.max_segment_count - 1:
                self.time_label.append(current_time)
            else:
                self.time_label[self.current_segment_number] = current_time
            [graph.ax.set_xticklabels([f'{round(tm, 1)}s' for tm in self.time_label]) for graph in self.graphs]
            self.total_segment_count += 1
            self.segment_signals_count = 0

    def plot_delta(self) -> None:
        if self.delta_graph.first_full:
            self.delta_graph.x1 = self.delta_graph.x1[1:len(self.delta_graph.x1)]
            self.delta_graph.y1 = self.delta_graph.y1[1:len(self.delta_graph.y1)]

        if self.delta_graph.second_full:
            self.delta_graph.x2 = self.delta_graph.x2[1:len(self.delta_graph.x2)]
            self.delta_graph.y2 = self.delta_graph.y2[1:len(self.delta_graph.y2)]

        if not self.delta_graph.first_full:
            self.delta_graph.lines.set_xdata(self.delta_graph.x1 + [None] * self.break_length + self.delta_graph.x2[self.break_length:])
            self.delta_graph.lines.set_ydata(self.delta_graph.y1 + [None] * self.break_length + self.delta_graph.y2[self.break_length:])

        if not self.delta_graph.second_full:
            self.delta_graph.lines.set_xdata(self.delta_graph.x2 + [None] * self.break_length + self.delta_graph.x1[self.break_length:])
            self.delta_graph.lines.set_ydata(self.delta_graph.y2 + [None] * self.break_length + self.delta_graph.y1[self.break_length:])

        delta_points_1 = self.delta_graph.ax.plot(self.delta_graph.x1, self.delta_graph.y1, 'b')
        delta_points_2 = self.delta_graph.ax.plot(self.delta_graph.x2, self.delta_graph.x2, 'b')

        for p1, p2 in zip(delta_points_1, delta_points_2):
            p1.remove()
            p2.remove()

    def plot_channels(self):
        if self.channels_graph.first_full:
            self.channels_graph.x1 = self.channels_graph.x1[1:len(self.channels_graph.x1)]
            self.channels_graph.y1 = self.channels_graph.y1[1:len(self.channels_graph.y1)]

            self.channels_graph.x1_b = self.channels_graph.x1_b[1:len(self.channels_graph.x1_b)]
            self.channels_graph.y1_b = self.channels_graph.y1_b[1:len(self.channels_graph.y1_b)]

        if self.channels_graph.second_full:
            self.channels_graph.x2 = self.channels_graph.x2[1:len(self.channels_graph.x2)]
            self.channels_graph.y2 = self.channels_graph.y2[1:len(self.channels_graph.y2)]

            self.channels_graph.x2_b = self.channels_graph.x2_b[1:len(self.channels_graph.x2_b)]
            self.channels_graph.y2_b = self.channels_graph.y2_b[1:len(self.channels_graph.y2_b)]

        if not self.channels_graph.first_full:
            self.channels_graph.lines.set_xdata(
                self.channels_graph.x1 + [None] * self.break_length + self.channels_graph.x2[self.break_length:])
            self.channels_graph.lines.set_ydata(
                self.channels_graph.y1 + [None] * self.break_length + self.channels_graph.y2[self.break_length:])

            self.channels_graph.lines_b.set_xdata(
                self.channels_graph.x1_b + [None] * self.break_length + self.channels_graph.x2_b[self.break_length:])
            self.channels_graph.lines_b.set_ydata(
                self.channels_graph.y1_b + [None] * self.break_length + self.channels_graph.y2_b[self.break_length:])

        if not self.channels_graph.second_full:
            self.channels_graph.lines.set_xdata(
                self.channels_graph.x2 + [None] * self.break_length + self.channels_graph.x1[self.break_length:])
            self.channels_graph.lines.set_ydata(
                self.channels_graph.y2 + [None] * self.break_length + self.channels_graph.y1[self.break_length:])

            self.channels_graph.lines_b.set_xdata(
                self.channels_graph.x2_b + [None] * self.break_length + self.channels_graph.x1_b[self.break_length:])
            self.channels_graph.lines_b.set_ydata(
                self.channels_graph.y2_b + [None] * self.break_length + self.channels_graph.y1_b[self.break_length:])

        channel_a_points_1 = self.channels_graph.ax.plot(self.channels_graph.x1, self.channels_graph.y1, 'r')
        channel_a_points_2 = self.channels_graph.ax.plot(self.channels_graph.x2, self.channels_graph.x2, 'r')

        channel_b_points_1 = self.channels_graph.ax.plot(self.channels_graph.x1_b, self.channels_graph.y1_b, 'b')
        channel_b_points_2 = self.channels_graph.ax.plot(self.channels_graph.x2_b, self.channels_graph.x2_b, 'b')

        for a1, a2, b1, b2 in zip(channel_a_points_1, channel_a_points_2, channel_b_points_1, channel_b_points_2):
            a1.remove()
            a2.remove()
            b1.remove()
            b2.remove()

    def add_points(self, delta_value: float, channel_a_value: float, channel_b_value: float) -> None:
        if not self.delta_graph.first_full:
            self.delta_graph.x1.append(self.current_step_number)
            self.delta_graph.y1.append(delta_value)

        if not self.delta_graph.second_full:
            self.delta_graph.x2.append(self.current_step_number)
            self.delta_graph.y2.append(delta_value)

        if not self.channels_graph.first_full:
            self.channels_graph.x1.append(self.current_step_number)
            self.channels_graph.y1.append(channel_a_value)

            self.channels_graph.x1_b.append(self.current_step_number)
            self.channels_graph.y1_b.append(channel_b_value)

        if not self.channels_graph.second_full:
            self.channels_graph.x2.append(self.current_step_number)
            self.channels_graph.y2.append(channel_a_value)

            self.channels_graph.x2_b.append(self.current_step_number)
            self.channels_graph.y2_b.append(channel_b_value)

    def check_iteration(self) -> None:
        for graph in self.graphs:
            if graph.is_first_iteration:
                graph.ax.set_ylim(graph.min, graph.max)
                graph.is_first_iteration = False

    def rescale_delta_graph_auto_mode(self):
        delta_graph_data = self.delta_graph.y1 + self.delta_graph.y2
        self.delta_graph.ax.set_ylim(min(delta_graph_data), max(delta_graph_data))

    def rescale_channels_graph_auto_mode(self):
        channels_graph_data = self.channels_graph.y1 + self.channels_graph.y2 \
                              + self.channels_graph.y1_b + self.channels_graph.y2_b
        self.channels_graph.ax.set_ylim(min(channels_graph_data), max(channels_graph_data))

    def rescale_delta_graph_manually(self):
        self.delta_graph.ax.set_ylim(self.delta_graph.min, self.delta_graph.max)

    def rescale_channels_graph_manually(self):
        self.channels_graph.ax.set_ylim(self.channels_graph.min, self.channels_graph.max)

    def switch_plots(self) -> None:
        for graph in self.graphs:
            if self.current_step_number % self.max_step_count == 0:
                self.current_step_number = 0
                graph.first_full, graph.second_full = graph.second_full, graph.first_full

    @staticmethod
    def iir_filter(array: list[int | float], b: float, a: float) -> list[float]:
        mean = sum(array) / len(array)
        filtered = signal.lfilter(b, a, [x - mean for x in array])
        return [e + mean for e in filtered]

    @staticmethod
    def decimate(array: list[int | float], rate: int) -> list[int | float]:
        return list(scipy.signal.decimate(array, rate, ftype='iir'))

    def get_delta(self) -> tuple[list[float], list[float], list[float]]:
        channel_a = [y[-1] for y in [self.iir_filter(x, self.b1_param, self.a1_param) for x in self.channel_a[-self.channel_window:]]]
        channel_b = [y[-1] for y in [self.iir_filter(x, self.b1_param, self.a1_param) for x in self.channel_b[-self.channel_window:]]]
        delta = self.iir_filter([x - y for x, y in zip(channel_a, channel_b)], self.b2_param, self.a2_param)
        return delta, channel_a, channel_b

    def get_intervals(self) -> None:
        prev = -1
        for e in self.channel_data:
            if 0 in e.channelAStarts:
                start = 0
            else:
                start = 1
            starts = list(sorted(list(e.channelAStarts) + list(e.channelBStarts)))
            self.segment_signals_count += len(e.channelData)
            for i in range(len(starts) - 1):
                if start == prev and i == 0:
                    if start == 0:
                        self.channel_a[-1] += e.channelData[starts[i]:starts[i + 1]]
                    else:
                        self.channel_b[-1] += e.channelData[starts[i]:starts[i + 1]]
                else:
                    if start == 0:
                        self.channel_a.append(e.channelData[starts[i]:starts[i + 1]])
                    if start == 1:
                        self.channel_b.append(e.channelData[starts[i]:starts[i + 1]])
                start = (start + 1) % 2
            if starts:
                if start == 0:
                    self.channel_a.append(e.channelData[starts[-1]:len(e.channelData)])
                if start == 1:
                    self.channel_b.append(e.channelData[starts[-1]:len(e.channelData)])
            prev = start

        self.last_signals.append([sum([len(e.channelData) for e in self.channel_data]), time.time()])
        self.last_signals = self.last_signals[-self.last_signals_range:]

    def get_value(self) -> tuple[float, float, float] | None:
        if not self.channel_data:
            return

        self.get_intervals()
        delta, channel_a, channel_b = self.get_delta()

        return delta[len(delta) - 1], channel_a[len(channel_a) - 1], channel_b[len(channel_b) - 1]

    def calculate_calibrated_value(self, delta):
        count = 0
        for i in range(len(self.calibration_data)):
            if self.calibration_data[i]['x'] == delta:
                return self.calibration_data[i]['y']
            if delta < self.calibration_data[i]['x']:
                break
            count += 1
        if count == 0:
            x_min, y_min = self.calibration_data[count]['x'], self.calibration_data[count]['y']
            x_min_2, y_min_2 = self.calibration_data[count + 1]['x'], self.calibration_data[count + 1]['y']
            return y_min_2 + (delta - x_min_2) * (y_min - y_min_2) / (x_min - x_min_2)
        if count == len(self.calibration_data):
            x_max, y_max = self.calibration_data[-1]['x'], self.calibration_data[-1]['y']
            x_max_2, y_max_2 = self.calibration_data[-2]['x'], self.calibration_data[-2]['y']
            return y_max_2 + (delta - x_max_2) * (y_max - y_max_2) / (x_max - x_max_2)
        if 0 < count < len(self.calibration_data):
            x_l, y_l = self.calibration_data[count - 1]['x'], self.calibration_data[count - 1]['y']
            x_r, y_r = self.calibration_data[count]['x'], self.calibration_data[count]['y']
            return (delta - x_l) * (y_r - y_l) / (x_r - x_l) + y_l

    def update_figure(self) -> None:
        while self.q1.qsize() > 0:
            print(self.q1.qsize())
            self.channel_data = []
            channel_data = [self.q1.get()]
            [self.graph_window.data.append(packet) for packet in channel_data]
            self.decode_packages(channel_data)
            delta_value, channel_a_value, channel_b_value = self.get_value() or (None, None, None)
            if delta_value is None or channel_a_value is None or channel_b_value is None:
                return
            old = delta_value
            delta_value = self.calculate_calibrated_value(delta_value)
            self.result1.append([self.segment_signals_count / 12000, delta_value, channel_a_value, channel_b_value, old])
        with open('data1', 'w') as f:
            f.write(json.dumps(self.result1, indent=4))
