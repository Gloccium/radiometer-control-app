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

        self.settings_window = SettingsWindow()
        self.graph_window = GraphWindow(self.settings_window)
        self.sending_window = SendingWindow(self.settings_window)

        self.graph_window.sending_window = self.sending_window
        self.sending_window.graph_window = self.graph_window

        self.tabs.addTab(self.graph_tab, "График")
        self.tabs.addTab(self.sending_tab, "Отправить исследование")
        self.tabs.addTab(self.settings_tab, "Настройки")

        self.graph_tab.layout = QGridLayout(self)
        self.graph_tab.layout.addWidget(self.graph_window.plot)
        self.graph_tab.layout.addWidget(self.graph_window.bounds_controls)
        self.graph_tab.layout.addWidget(self.graph_window.filename)
        self.graph_tab.layout.addWidget(self.graph_window.select_local_calibration_button)
        self.graph_tab.layout.addWidget(self.graph_window.select_device_button)
        self.graph_tab.layout.addWidget(self.graph_window.add_device_button)
        self.graph_tab.layout.addWidget(self.graph_window.add_calibration_button)
        self.graph_tab.layout.addWidget(self.graph_window.port_list)
        self.graph_tab.layout.addWidget(self.graph_window.controls)
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
        self.sending_tab.layout.addWidget(self.sending_window.description)
        self.sending_tab.layout.addWidget(self.sending_window.send_measurement_button)
        self.sending_tab.layout.addStretch()
        self.sending_tab.setLayout(self.sending_tab.layout)

        self.settings_tab.layout = QVBoxLayout(self)
        self.settings_tab.layout.addWidget(self.settings_window.server_address_label)
        self.settings_tab.layout.addWidget(self.settings_window.server_address_input)
        self.settings_tab.layout.addWidget(self.settings_window.records_directory)
        self.settings_tab.layout.addWidget(self.settings_window.records_directory_button)
        self.settings_tab.layout.addWidget(self.settings_window.calibration_directory)
        self.settings_tab.layout.addWidget(self.settings_window.calibration_directory_button)
        self.settings_tab.layout.addWidget(self.settings_window.delta_graph_bounds)
        self.settings_tab.layout.addWidget(self.settings_window.channels_graph_bounds)
        self.settings_tab.layout.addWidget(self.settings_window.save_button)
        self.settings_tab.layout.addStretch()
        self.settings_tab.setLayout(self.settings_tab.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()
