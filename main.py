import sys

from mainwindow import MainWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # from PySide6.QtCore import Qt
    # app.setLayoutDirection(Qt.RightToLeft)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
