from PyQt5.QtWidgets import QGridLayout, QWidget


class SquareLayout(QWidget):
    def __init__(self, element_0_0, element_0_1, element_1_0, element_1_1):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(element_0_0, 0, 0)
        layout.addWidget(element_0_1, 0, 1)
        layout.addWidget(element_1_0, 1, 0)
        layout.addWidget(element_1_1, 1, 1)
