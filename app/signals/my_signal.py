from PyQt5 import QtCore


class MySignal(QtCore.QObject):
    sig_no_args = QtCore.pyqtSignal()
    sig_with_str = QtCore.pyqtSignal(str)
