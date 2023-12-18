from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class Timer(QObject):
    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.is_running = False
        self.m_id = self.startTimer(1)

    def timerEvent(self, event):
        if self.m_id == event.timerId():
            pass
        super().timerEvent(event)

    def stop(self):
        self.is_running = False

    @QtCore.pyqtSlot()
    def start(self):
        self.is_running = True
        while self.is_running:
            self.graph.signal.sig_no_args.emit()
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(self.graph.update_rate_ms, loop.quit)
            loop.exec()
