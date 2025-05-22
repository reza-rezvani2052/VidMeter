# clickablevideowidget.py

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtMultimediaWidgets import QVideoWidget


class ClickableVideoWidget(QVideoWidget):
    clicked = Signal()
    doubleClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self.clicked.emit)

        self.mainwindow: MainWindow = self.parent().parent()  # MainWindow
        # print(type(self.mainwindow ))
        # print(self.mainwindow.objectName())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._click_timer.start(250)  # اگر ظرف 250ms دوبار کلیک نشد، clicked رو emit کن

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._click_timer.stop()  # اگر دوبار کلیک شد، کلیک معمولی رو لغو کن
            self.doubleClicked.emit()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Space:
            self.clicked.emit()  # برای Play/Pause

        elif event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)

        elif event.key() == Qt.Key_Right:
            self.mainwindow.seek_relative(5000)  # جلو ۵ ثانیه

        elif event.key() == Qt.Key_Left:
            self.mainwindow.seek_relative(-5000)  # عقب ۵ ثانیه

        elif event.key() == Qt.Key_Up:
            self.mainwindow.adjust_volume(+5)

        elif event.key() == Qt.Key_Down:
            self.mainwindow.adjust_volume(-5)

        elif event.key() == Qt.Key_M:
            self.mainwindow.toggle_mute()

        elif event.key() == Qt.Key_F:
            self.mainwindow.toggle_fullscreen()

        else:
            super().keyPressEvent(event)
