from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit


class OffsetParameter(QWidget):
    def __init__(self, text):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.offset_label = QLabel(text)
        self.offset_label.setFixedWidth(300)
        layout.addWidget(self.offset_label)

        self.offset_value = QLineEdit()
        self.offset_value.setValidator(QIntValidator(1, 9999, self))
        layout.addWidget(self.offset_value)
