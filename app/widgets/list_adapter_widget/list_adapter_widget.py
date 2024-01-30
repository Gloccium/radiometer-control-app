from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QHBoxLayout


class ListAdapter(QWidget):
    def __init__(self, parent=None):
        super(ListAdapter, self).__init__(parent)

        self.vBox = QVBoxLayout()
        self.name = QLabel()
        self.vBox.addWidget(self.name)

        self.vBoxSecond = QVBoxLayout()
        self.description = QLabel()
        self.vBoxSecond.addWidget(self.description)

        self.hBox = QHBoxLayout()
        self.hBox.addLayout(self.vBox)
        self.hBox.addLayout(self.vBoxSecond)
        self.setLayout(self.hBox)

    def set_name(self, text):
        self.name.setText(text)

    def set_description(self, text):
        self.description.setText(text)
