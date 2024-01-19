from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QGridLayout

from app.windows.graph_window import GraphWindow
from app.windows.sending_window import SendingWindow


class TabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.graph_tab = QWidget()
        self.sending_tab = QWidget()
        self.tabs.resize(1600, 1200)

        self.graph_window = GraphWindow()
        self.sending_window = SendingWindow()

        self.tabs.addTab(self.graph_tab, "Graph")
        self.tabs.addTab(self.sending_tab, "Sending")

        self.graph_tab.layout = QGridLayout(self)
        self.graph_tab.layout.addWidget(self.graph_window.plot)
        self.graph_tab.layout.addWidget(self.graph_window.start_device_button)
        self.graph_tab.layout.addWidget(self.graph_window.stop_button)
        self.graph_tab.layout.addWidget(self.graph_window.update_port_button)
        [self.graph_tab.layout.addWidget(button) for button in self.graph_window.port_buttons]
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
        self.sending_tab.setLayout(self.sending_tab.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()
