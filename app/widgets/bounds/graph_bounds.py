from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout


class GraphBounds(QWidget):
    def __init__(self, min_text, max_text, previous_min_value, previous_max_value):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        self.min_label = QLabel(min_text)
        self.min_label.setFixedWidth(300)
        layout.addWidget(self.min_label, 0, 0)

        self.previous_min_value = previous_min_value
        self.min_value = QLineEdit()
        layout.addWidget(self.min_value, 0, 1)

        self.max_label = QLabel(max_text)
        self.max_label.setFixedWidth(300)
        layout.addWidget(self.max_label, 1, 0)

        self.previous_max_value = previous_max_value
        self.max_value = QLineEdit()
        layout.addWidget(self.max_value, 1, 1)
