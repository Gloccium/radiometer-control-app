from PyQt5.QtWidgets import QWidget


class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1280, 720)
        self.show()
