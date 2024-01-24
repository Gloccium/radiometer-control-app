from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QPushButton
from serial import Serial, SerialException

from app.threads.device_controller import DeviceController
from app.threads.timer import Timer
from app.widgets.graph_widget.graph_widget import GraphWidget


class GraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.plot = None
        self.start_button = None
        self.pause_button = None
        self.toggle_channels_button = None
        self.finish_button = None
        self.data = []
        self.is_paused = False

        self.device_thread = QThread()
        self.device_controller = DeviceController()
        self.device_controller.moveToThread(self.device_thread)
        self.device_thread.started.connect(self.device_controller.run)

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
        if self.device_controller.port != '':
            try:
                serial = Serial(self.device_controller.port, baudrate=self.device_controller.baudrate)
                serial.reset_input_buffer()
                serial.close()
            except SerialException:
                print('Could not open port')
                return
            self.device_thread.start()
            self.timer_thread.start()
            self.pause_button.setDisabled(False)
            self.finish_button.setDisabled(False)
            self.start_button.setDisabled(True)

    def write_data(self):
        with open('../data', 'wb') as f:
            [f.write(s) for s in self.data]

    def pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.timer.stop()
            self.timer_thread.quit()
            self.pause_button.setText('Continue')
        else:
            self.timer_thread.start()
            self.pause_button.setText('Pause')

    def finish(self):
        self.timer.stop()
        self.timer_thread.quit()
        self.device_thread.quit()
        self.write_data()
        self.start_button.setDisabled(False)
        self.pause_button.setText('Pause')
        self.is_paused = False
        self.pause_button.setDisabled(True)
        self.finish_button.setDisabled(True)
        self.plot.reinitialize_plot()
        self.device_controller.stop()

    def toggle_channels(self):
        self.plot.toggle_channels()
        if self.plot.is_channels_visible:
            self.toggle_channels_button.setText('Hide channels')
        else:
            self.toggle_channels_button.setText('Show channels')

    def init_control_buttons(self) -> None:
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_device)

        self.pause_button = QPushButton('Pause', self)
        self.pause_button.clicked.connect(self.pause)
        self.pause_button.setDisabled(True)

        self.toggle_channels_button = QPushButton('Hide channels', self)
        self.toggle_channels_button.clicked.connect(self.toggle_channels)

        self.finish_button = QPushButton('Finish', self)
        self.finish_button.clicked.connect(self.finish)
        self.finish_button.setDisabled(True)
