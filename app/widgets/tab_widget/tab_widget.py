from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QGridLayout

from app.windows.device_window import DeviceWindow
from app.windows.graph_window import GraphWindow
from app.windows.sending_window import SendingWindow
from app.windows.settings_window import SettingsWindow


class TabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.graph_tab = QWidget()
        self.sending_tab = QWidget()
        self.settings_tab = QWidget()
        self.tabs.resize(1600, 1200)

        self.graph_window = GraphWindow()
        self.settings_window = SettingsWindow(self.graph_window)
        self.sending_window = SendingWindow(self.settings_window)

        self.tabs.addTab(self.graph_tab, "Graph")
        self.tabs.addTab(self.sending_tab, "Sending")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.graph_tab.layout = QGridLayout(self)
        self.graph_tab.layout.addWidget(self.graph_window.plot)
        self.graph_tab.layout.addWidget(self.graph_window.toggle_channels_button)
        self.graph_tab.layout.addWidget(self.graph_window.start_button)
        self.graph_tab.layout.addWidget(self.graph_window.finish_button)
        self.graph_tab.setLayout(self.graph_tab.layout)

        self.sending_tab.layout = QVBoxLayout(self)
        self.sending_tab.layout.addWidget(self.sending_window.login)
        self.sending_tab.layout.addWidget(self.sending_window.password)
        self.sending_tab.layout.addWidget(self.sending_window.login_button)
        self.sending_tab.layout.addWidget(self.sending_window.date)
        self.sending_tab.layout.addWidget(self.sending_window.time)
        self.sending_tab.layout.addWidget(self.sending_window.patient)
        self.sending_tab.layout.addWidget(self.sending_window.patient_list)
        self.sending_tab.layout.addWidget(self.sending_window.add_patient_button)
        self.sending_tab.layout.addWidget(self.sending_window.device)
        self.sending_tab.layout.addWidget(self.sending_window.device_list)
        self.sending_tab.layout.addWidget(self.sending_window.add_device_button)
        self.sending_tab.layout.addWidget(self.sending_window.description)
        self.sending_tab.layout.addWidget(self.sending_window.send_measurement_button)
        self.sending_tab.layout.addStretch()
        self.sending_tab.setLayout(self.sending_tab.layout)

        self.settings_tab.layout = QVBoxLayout(self)
        self.settings_tab.layout.addWidget(self.settings_window.server_label)
        self.settings_tab.layout.addWidget(self.settings_window.server_address)
        self.settings_tab.layout.addStretch()
        self.settings_tab.layout.addWidget(self.settings_window.ports_label)
        [self.settings_tab.layout.addWidget(button) for button in self.settings_window.port_buttons]
        self.settings_tab.layout.addWidget(self.settings_window.update_port_button)
        self.settings_tab.layout.addStretch()
        self.settings_tab.setLayout(self.settings_tab.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()
