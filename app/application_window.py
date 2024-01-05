from PyQt5.QtWidgets import QWidget
from app.tab_widget import TabWidget


class ApplicationWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.tab_widget = TabWidget(self)
        self.show()
