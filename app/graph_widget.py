from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, channel_data=None):
        if channel_data is None:
            channel_data = []
        self.x = []
        self.y = []
        self.count = 0
        self.channel_data = channel_data
        fig = Figure(figsize=(8, 6), dpi=100)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.init_plot()

    def plot(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(300)

    def init_plot(self):
        self.axes.plot(self.x, self.y)

    def update_figure(self):
        self.x.append(self.count)
        self.y.append(sum(self.channel_data[self.count]) / len((self.channel_data[self.count])))
        self.count += 1
        self.axes.cla()
        self.axes.plot(self.x, self.y)
        self.draw()
