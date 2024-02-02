from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.server_label = QLabel(self)
        self.server_address = QLineEdit(self)
        self.element_width = 200

        self.configure_elements()

    def configure_elements(self) -> None:
        self.server_label.setText('Server address')
        self.server_label.setStyleSheet("QLabel{font-size: 14pt;}")

        self.server_address.setMaximumWidth(self.element_width)