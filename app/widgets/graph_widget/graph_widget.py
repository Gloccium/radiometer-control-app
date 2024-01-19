import base64
import binascii
import time

from PyQt5.QtWidgets import QSizePolicy
from google.protobuf.message import DecodeError
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy import signal

from app.widgets.graph_widget.graph_data import GraphData
from app.messages import message_pb2
from app.signals.my_signal import MySignal


class GraphWidget(FigureCanvas):
    def __init__(self, parent=None, device_controller=None):
        self.parent = parent

        self.update_rate_ms = 200
        self.current_step_number = 0
        self.max_step_count = 100
        self.current_segment_number = 0
        self.max_segment_count = 5
        self.total_segment_count = 0
        self.time_label = [0.0]
        self.break_length = 3
        self.rescale_sensitivity = 2

        self.device_controller = device_controller
        self.channel_data = []
        self.channel_window = 1000
        self.channel_a = []
        self.channel_b = []

        self.b1_param, self.a1_param = signal.iirfilter(2, 10, ftype='butter', btype='lowpass', fs=12000)
        self.b2_param, self.a2_param = signal.iirfilter(2, 0.1, ftype='butter', btype='lowpass', fs=400)
        self.decimation_rate = 10

        self.previous_value = 0
        self.error_count = 0
        self.package_count = 0

        self.figure, (self.delta_ax, self.channel_a_ax, self.channel_b_ax) = plt.subplots(1, 3, figsize=(21, 9))
        self.delta_ax.set_title("Delta")
        self.channel_a_ax.set_title("Channel A")
        self.channel_b_ax.set_title("Channel B")
        plt.subplots_adjust(left=0.02, right=0.98)
        self.delta_lines, = self.delta_ax.plot([], [], 'r')
        self.channel_a_lines, = self.channel_a_ax.plot([], [], 'g')
        self.channel_b_lines, = self.channel_b_ax.plot([], [], 'b')

        self.delta_graph = GraphData(self.delta_ax, self.delta_lines, 100)
        self.channel_a_graph = GraphData(self.channel_a_ax, self.channel_a_lines, 1000)
        self.channel_b_graph = GraphData(self.channel_b_ax, self.channel_b_lines, 1000)
        self.graphs = [self.delta_graph, self.channel_a_graph, self.channel_b_graph]

        FigureCanvas.__init__(self, self.figure)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.setParent(parent)

        self.signal = MySignal()
        self.signal.sig_no_args.connect(self.update_figure)

        self.time_ms = 0
        self.configure_plot()

    def configure_plot(self) -> None:
        for graph in self.graphs:
            graph.ax.set_xlim(0, self.max_step_count)
            graph.ax.set_xticklabels([f'{round(t, 1)}s' for t in self.time_label])

    def get_packages(self) -> None:
        self.channel_data = []
        channel_data = [self.device_controller.channel_data.get()
                        for _ in range(self.device_controller.channel_data.qsize())]
        [self.parent.data.append(packet) for packet in channel_data]
        self.decode_packages(channel_data)

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

    def update_x_label(self) -> None:
        if self.current_step_number % (self.max_step_count // self.max_segment_count) == 0:
            interval = time.time() - self.time_ms
            self.time_ms = time.time()
            self.current_segment_number = (self.current_segment_number + 1) % self.max_segment_count
            current_time = self.time_label[self.current_segment_number - 1] + interval
            if self.total_segment_count < self.max_segment_count - 1:
                self.time_label.append(current_time)
            else:
                self.time_label[self.current_segment_number] = current_time
            [graph.ax.set_xticklabels([f'{round(tm, 1)}s' for tm in self.time_label]) for graph in self.graphs]
            self.total_segment_count += 1

    def plot_data(self) -> None:
        for graph in self.graphs:
            if graph.first_full:
                graph.x1 = graph.x1[1:len(graph.x1)]
                graph.y1 = graph.y1[1:len(graph.y1)]

            if graph.second_full:
                graph.x2 = graph.x2[1:len(graph.x2)]
                graph.y2 = graph.y2[1:len(graph.y2)]

            if not graph.first_full:
                graph.lines.set_xdata(graph.x1 + [None] * self.break_length + graph.x2[self.break_length:])
                graph.lines.set_ydata(graph.y1 + [None] * self.break_length + graph.y2[self.break_length:])

            if not graph.second_full:
                graph.lines.set_xdata(graph.x2 + [None] * self.break_length + graph.x1[self.break_length:])
                graph.lines.set_ydata(graph.y2 + [None] * self.break_length + graph.y1[self.break_length:])

            points1 = graph.ax.plot(graph.x1, graph.y1, 'b')
            points2 = graph.ax.plot(graph.x2, graph.x2, 'b')

            for p1, p2 in zip(points1, points2):
                p1.remove()
                p2.remove()

    def add_points(self, delta_value: float, channel_a_value: float, channel_b_value: float) -> None:
        for graph, value in zip(self.graphs, [delta_value, channel_a_value, channel_b_value]):
            if not graph.first_full:
                graph.x1.append(self.current_step_number)
                graph.y1.append(value)

            if not graph.second_full:
                graph.x2.append(self.current_step_number)
                graph.y2.append(value)

    def check_iteration(self) -> None:
        for graph in self.graphs:
            if graph.is_first_iteration:
                self.time_ms = time.time()
                graph.ax.set_ylim(graph.y1[0] - graph.offset, graph.y1[0] + graph.offset)
                graph.last_scaled_y_value = graph.y1[0]
                graph.is_first_iteration = False

    def rescale(self) -> None:
        for graph in self.graphs:
            if not graph.first_full and (graph.y1[-1] > graph.last_scaled_y_value + graph.offset / self.rescale_sensitivity
                                         or graph.y1[-1] < graph.last_scaled_y_value - graph.offset / self.rescale_sensitivity):
                graph.last_scaled_y_value = graph.y1[-1]
                graph.ax.set_ylim(graph.y1[-1] - graph.offset, graph.y1[-1] + graph.offset)

            if not graph.second_full and (graph.y2[-1] > graph.last_scaled_y_value + graph.offset / self.rescale_sensitivity
                                         or graph.y2[-1] < graph.last_scaled_y_value - graph.offset / self.rescale_sensitivity):
                graph.last_scaled_y_value = graph.y2[-1]
                graph.ax.set_ylim(graph.y2[-1] - graph.offset, graph.y2[-1] + graph.offset)

    def switch_plots(self) -> None:
        for graph in self.graphs:
            if self.current_step_number % self.max_step_count == 0:
                self.current_step_number = 0
                graph.first_full, graph.second_full = graph.second_full, graph.first_full
                if graph.first_full:
                    graph.ax.set_ylim(graph.y1[-1] - graph.offset, graph.y1[-1] + graph.offset)
                if graph.second_full:
                    graph.ax.set_ylim(graph.y2[-1] - graph.offset, graph.y2[-1] + graph.offset)

    @staticmethod
    def iir_filter(array: list[int | float], b: float, a: float) -> list[float]:
        mean = sum(array) / len(array)
        filtered = signal.lfilter(b, a, [x - mean for x in array])
        return [e + mean for e in filtered]

    @staticmethod
    def decimate(array: list[int | float], rate: int) -> list[int | float]:
        return [array[i] for i in range(0, len(array), rate)]

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
            if start == 0:
                self.channel_a.append(e.channelData[starts[-1]:len(e.channelData)])
            if start == 1:
                self.channel_b.append(e.channelData[starts[-1]:len(e.channelData)])
            prev = start

    def get_value(self) -> tuple[float, float, float] | None:
        if not self.channel_data:
            return

        self.get_intervals()
        delta, channel_a, channel_b = self.get_delta()

        return delta[len(delta) - 1], channel_a[len(channel_a) - 1], channel_b[len(channel_b) - 1]

    def update_figure(self) -> None:
        self.get_packages()
        delta_value, channel_a_value, channel_b_value = self.get_value() or (None, None, None)

        if delta_value is None or channel_a_value is None or channel_b_value is None:
            return

        self.current_step_number += 1
        self.add_points(delta_value, channel_a_value, channel_b_value)
        self.check_iteration()
        self.rescale()
        self.switch_plots()
        self.plot_data()

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.update_x_label()
