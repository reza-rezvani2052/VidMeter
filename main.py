import os
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

    splash_image_path = os.path.join(os.path.dirname(__file__) + "/rc", 'splash.png')
    print(f"splash_image_path = {splash_image_path}")  #TODO: در انتشار نهایی این را حذف کنم
    if os.path.exists(splash_image_path):
        splash_pix = QPixmap(splash_image_path)
    else:
        splash_pix = QPixmap("./_internal/splash.png")

    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    #  اجازه میدیم کمی سیستم پردازش کنه
    app.processEvents()

    # time.sleep(3)

    # ...
    from mainwindow import MainWindow

    window = MainWindow()
    window.show()
    # ...

    splash.finish(window)

    sys.exit(app.exec())
