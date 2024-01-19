from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QPushButton

from app.threads.device_controller import DeviceController
from app.threads.timer import Timer
from app.widgets.graph_widget.graph_widget import GraphWidget


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.plot = None
        self.start_button = None
        self.stop_button = None
        self.data = []

        self.device_thread = QThread()
        self.device_controller = DeviceController()
        self.device_controller.moveToThread(self.device_thread)
        self.device_thread.started.connect(self.device_controller.load_data)

        self.init_plot()

        self.timer_thread = QThread()
        self.timer = Timer(self.plot)
        self.timer.moveToThread(self.timer_thread)
        self.timer_thread.started.connect(self.timer.start)

        self.init_control_buttons()

    def init_plot(self) -> None:
        self.plot = GraphWidget(self, device_controller=self.device_controller)
        self.plot.move(0, 0)

    def start_device(self) -> None:
        self.device_thread.start()
        self.timer_thread.start()
        if self.device_controller.port_error:
            print('Could not open port')
            self.device_thread.quit()
            self.timer_thread.quit()

    def write_data(self):
        with open('../data', 'wb') as f:
            [f.write(s) for s in self.data]

    def stop(self):
        self.timer.stop()
        self.write_data()

    def init_control_buttons(self) -> None:
        self.start_button = QPushButton('Start', self)
        self.start_button.move(100, 1000)
        self.start_button.resize(140, 60)
        self.start_button.clicked.connect(self.start_device)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.move(300, 1000)
        self.stop_button.resize(140, 100)
        self.stop_button.clicked.connect(self.stop)
