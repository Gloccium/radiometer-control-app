import serial.tools.list_ports
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit


class SettingsWindow(QWidget):
    def __init__(self, graph_window):
        super().__init__()
        self.graph_window = graph_window
        self.ports_label = QLabel(self)
        self.server_label = QLabel(self)
        self.server_address = QLineEdit(self)
        self.element_width = 200

        self.selected_port = ''
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]
        self.port_buttons = [QPushButton(f'COM{i}', self) for i in range(1, 17)]
        self.update_port_button = QPushButton('Update', self)

        self.configure_elements()
        self.configure_port_buttons()
        self.init_control_buttons()

    def configure_elements(self) -> None:
        self.ports_label.setText('COM-ports')
        self.ports_label.setStyleSheet("QLabel{font-size: 14pt;}")

        self.server_label.setText('Server address')
        self.server_label.setStyleSheet("QLabel{font-size: 14pt;}")

        self.server_address.setMaximumWidth(self.element_width)

    def init_control_buttons(self) -> None:
        self.update_port_button.setMaximumWidth(self.element_width)
        self.update_port_button.clicked.connect(self.update_ports)

    def update_ports(self) -> None:
        self.active_ports = [port.name for port in serial.tools.list_ports.comports()]
        self.configure_port_buttons()

    def select_port(self, port: str) -> None:
        self.selected_port = port
        self.graph_window.device_controller.port = self.selected_port
        self.configure_port_buttons()

    def configure_port_buttons(self) -> None:
        for i in range(len(self.port_buttons)):
            if self.port_buttons[i].text() in self.active_ports:
                self.port_buttons[i].disconnect()
                self.port_buttons[i].clicked.connect(lambda x, i=i: self.select_port(self.port_buttons[i].text()))
                self.port_buttons[i].setStyleSheet(f'QPushButton {{background-color: '
                                                   f'{"#008000" if self.port_buttons[i].text() == self.selected_port else "#FFFFFF"} }}')
                self.port_buttons[i].setMaximumWidth(self.element_width)
                self.port_buttons[i].show()
            else:
                self.port_buttons[i].hide()
