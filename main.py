import sys
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


# ----------------------------------------------------------------------------

def build_ui_and_convert_qrc_to_py():
    from build_ui import convert_qrc_to_py, convert_all_ui_files

    convert_qrc_to_py()
    convert_all_ui_files()


# TODO: در رلیز نهایی برنامه، بعد از ساخت فایل مربوطه، خط زیر غیر فعال شود
build_ui_and_convert_qrc_to_py()
import resources_rc  # پای چارم به اشتباه این را گاستفاده نشدهگ در نظر میگیره

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # from PySide6.QtCore import Qt
    # app.setLayoutDirection(Qt.RightToLeft)

    # ...

    splash = QSplashScreen(QPixmap(":/splash.jpg"), Qt.WindowStaysOnTopHint)
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
