from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QGridLayout

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
        self.graph_tab.layout.addWidget(self.graph_window.pause_button)
        self.graph_tab.layout.addWidget(self.graph_window.finish_button)
        self.graph_tab.setLayout(self.graph_tab.layout)

        self.sending_tab.layout = QVBoxLayout(self)
        self.sending_tab.layout.addWidget(self.sending_window.surname_input)
        self.sending_tab.layout.addWidget(self.sending_window.name_input)
        self.sending_tab.layout.addWidget(self.sending_window.patronymic_input)
        self.sending_tab.layout.addWidget(self.sending_window.date_input)
        self.sending_tab.layout.addWidget(self.sending_window.time_input)
        self.sending_tab.layout.addWidget(self.sending_window.patient_input)
        self.sending_tab.layout.addWidget(self.sending_window.device_input)
        self.sending_tab.layout.addWidget(self.sending_window.description_input)
        self.sending_tab.layout.addWidget(self.sending_window.send_button)
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
