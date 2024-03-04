from PyQt5 import QtCore
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout


class GraphBounds(QWidget):
    def __init__(self, min_text, max_text):
        super().__init__()
        self.double_validator = QDoubleValidator()
        self.double_validator.setNotation(QDoubleValidator.StandardNotation)
        self.double_validator.setLocale(QtCore.QLocale("en_US"))
        self.double_validator.setBottom(-9999)
        self.double_validator.setTop(9999)
        self.double_validator.setDecimals(2)

        layout = QGridLayout()
        self.setLayout(layout)

        self.min_label = QLabel(min_text)
        self.min_label.setFixedWidth(300)
        layout.addWidget(self.min_label, 0, 0)

        self.min_value = QLineEdit()
        self.min_value.setValidator(self.double_validator)
        layout.addWidget(self.min_value, 0, 1)

        self.max_label = QLabel(max_text)
        self.max_label.setFixedWidth(300)
        layout.addWidget(self.max_label, 1, 0)

        self.max_value = QLineEdit()
        self.max_value.setValidator(self.double_validator)
        layout.addWidget(self.max_value, 1, 1)
