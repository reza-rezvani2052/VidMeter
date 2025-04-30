import sys
# import time
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # from PySide6.QtCore import Qt
    # app.setLayoutDirection(Qt.RightToLeft)

    # ...

    splash_pix = QPixmap("splash.png")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    #  اجازه بده کمی سیستم پردازش کنه
    app.processEvents()

    # time.sleep(3)

    # ...
    from mainwindow import MainWindow

    window = MainWindow()
    window.show()
    # ...

    splash.finish(window)

    sys.exit(app.exec())
