from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QHBoxLayout


class SingleListAdapter(QWidget):
    def __init__(self, parent=None):
        super(SingleListAdapter, self).__init__(parent)

        self.vBox = QVBoxLayout()
        self.name = QLabel()
        self.vBox.addWidget(self.name)

        self.hBox = QHBoxLayout()
        self.hBox.addLayout(self.vBox)
        self.setLayout(self.hBox)

    def set_name(self, text):
        self.name.setText(text)
