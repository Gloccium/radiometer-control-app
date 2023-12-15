from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSizePolicy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, channel_data=None):
        if channel_data is None:
            channel_data = []
        self.x = []
        self.y = []
        self.count = 0
        self.plot_range = 100
        self.update_rate = 10
        self.channel_data = channel_data
        self.previous_value = sum(self.channel_data[self.count]) / len(self.channel_data[self.count])

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

    def update_figure(self):
        self.x.append(self.count)
        current_value = self.previous_value * 0.999 + sum(self.channel_data[self.count]) / len((self.channel_data[self.count])) * 0.001
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

