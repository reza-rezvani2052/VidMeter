# mainwindow.py

import os
import sys

from ui_mainwindow import Ui_MainWindow

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableWidgetItem
)

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

# برای اصلاح نوشته های فارسی در نمودار
import arabic_reshaper
from bidi.algorithm import get_display

from video_worker import VideoWorker


# ========================================================================================


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # دکمه‌ها در شروع مخفی باشند
        self.ui.progressBar.setVisible(False)
        self.ui.btnPauseResume.setVisible(False)
        self.ui.btnCancelProcess.setVisible(False)

        # دکمه‌ها
        self.ui.btnSelectPath.clicked.connect(self.select_path)
        self.ui.btnSelectFiles.clicked.connect(self.select_files)
        self.ui.btnSaveToFile.clicked.connect(self.save_to_file)
        self.ui.btnChart.clicked.connect(self.show_chart)
        self.ui.btnPauseResume.clicked.connect(self.toggle_pause_resume)
        self.ui.btnCancelProcess.clicked.connect(self.cancel_process)

        self.ui.tableFiles.itemSelectionChanged.connect(self.update_selected_duration)

        self.worker = None
        self.is_paused = False

        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Vazir.ttf")
        if os.path.exists(font_path):
            rcParams['font.family'] = 'Vazir'
            plt.rcParams['font.family'] = 'Vazir'

    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not path:
            return

        self.ui.statusbar.showMessage(path)

        file_list = self.get_video_files(path, check_subfolders=self.ui.chkSubfolder.isChecked())
        if file_list:
            self.start_worker(file_list)

    def select_files(self):
        path, _ = QFileDialog.getOpenFileNames(
            self, "Select Video File(s)", "", "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv)"
        )
        if not path:
            return
        else:
            self.ui.statusbar.showMessage(os.path.dirname(path[0]))
            self.start_worker(path)

    def set_buttons_enable(self, is_enable=True):
        self.ui.btnSelectFiles.setEnabled(is_enable)
        self.ui.btnSelectPath.setEnabled(is_enable)
        self.ui.btnChart.setEnabled(is_enable)
        self.ui.btnSaveToFile.setEnabled(is_enable)
        # self.ui.btnPauseResume.setEnabled(not is_enable)
        # self.ui.btnCancelProcess.setEnabled(not is_enable)

    @staticmethod
    def get_video_files(path, check_subfolders=False, ignore_errors=True):
        video_files = []
        video_ext = ['.mp4', '.avi', '.mkv', '.wmv', '.mov']

        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"مسیر '{path}' وجود ندارد.")

            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in video_ext:
                    return [path]
                return []

            if check_subfolders:
                for root, _, files in os.walk(path):
                    for f in files:
                        if os.path.splitext(f)[1].lower() in video_ext:
                            video_files.append(os.path.join(root, f))
            else:
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if os.path.isfile(full_path):
                        if os.path.splitext(entry)[1].lower() in video_ext:
                            video_files.append(full_path)

            return video_files

        except Exception as e:
            if not ignore_errors:
                raise
            print(f"خطا در پردازش مسیر '{path}': {str(e)}")
            return []

    def start_worker(self, file_list):
        self.set_buttons_enable(False)

        self.ui.tableFiles.setRowCount(0)

        # نمایش progress bar و دکمه‌های کنترل
        self.ui.progressBar.setVisible(True)
        self.ui.btnPauseResume.setVisible(True)
        self.ui.btnCancelProcess.setVisible(True)

        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setMaximum(len(file_list))

        self.worker = VideoWorker(file_list)
        self.worker.progress.connect(self.ui.progressBar.setValue)
        self.worker.result.connect(self.populate_table)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

        self.ui.btnPauseResume.setText("⏸")
        self.is_paused = False

    def toggle_pause_resume(self):
        if not self.worker:
            return

        if self.is_paused:
            self.worker.resume()
            self.ui.btnPauseResume.setText("⏸")
        else:
            self.worker.pause()
            self.ui.btnPauseResume.setText("▶️")

        self.is_paused = not self.is_paused

    def cancel_process(self):
        if self.worker:
            self.worker.cancel()

    def worker_finished(self):
        self.set_buttons_enable(True)   #TODO: ***
        #...
        # مخفی‌سازی دکمه‌ها و نوار پیشرفت
        self.ui.progressBar.setVisible(False)
        self.ui.btnPauseResume.setVisible(False)
        self.ui.btnCancelProcess.setVisible(False)

    def calculate_total_duration(self):
        total_seconds = 0
        for row in range(self.ui.tableFiles.rowCount()):
            duration_text = self.ui.tableFiles.item(row, 1).text()
            h, m, s = map(int, duration_text.split(':'))
            total_seconds += h * 3600 + m * 60 + s
        return total_seconds

    def update_selected_duration(self):
        selected_ranges = self.ui.tableFiles.selectedRanges()
        total_seconds = 0

        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                item = self.ui.tableFiles.item(row, 1)  # ستون 1 = Duration
                if item:
                    h, m, s = map(int, item.text().split(':'))
                    total_seconds += h * 3600 + m * 60 + s

        total_text = self.format_duration(total_seconds)
        self.ui.statusbar.showMessage(f"مدت‌زمان انتخاب‌شده: {total_text}")

    def populate_table(self, results):
        self.results = results
        self.ui.tableFiles.setRowCount(len(results))
        self.ui.tableFiles.setColumnCount(2)
        self.ui.tableFiles.setHorizontalHeaderLabels(["File Name", "Duration"])

        for i, (name, duration) in enumerate(results):
            self.ui.tableFiles.setItem(i, 0, QTableWidgetItem(name))
            self.ui.tableFiles.setItem(i, 1, QTableWidgetItem(f"{self.format_duration(duration)}"))

        self.ui.tableFiles.resizeColumnsToContents()

        total_duration = self.calculate_total_duration()
        total_text = self.format_duration(total_duration)

        self.ui.statusbar.showMessage(f"مجموع مدت‌زمان همه ویدیوها: {total_text}")


    @staticmethod
    def format_duration(seconds):
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02}:{mins:02}:{secs:02}"

    def save_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text File (*.txt);;CSV File (*.csv)")
        if not path:
            return

        with open(path, 'w', encoding='utf-8') as f:
            for row in range(self.ui.tableFiles.rowCount()):
                filename = self.ui.tableFiles.item(row, 0).text()
                duration = self.ui.tableFiles.item(row, 1).text()
                f.write(f"{filename}, {duration}\n")

    def show_chart(self):
        filenames = []
        durations = []

        for row in range(self.ui.tableFiles.rowCount()):
            filenames.append(self.ui.tableFiles.item(row, 0).text())
            h, m, s = map(int, self.ui.tableFiles.item(row, 1).text().split(':'))
            total_seconds = h * 3600 + m * 60 + s
            durations.append(total_seconds)

        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Vazir.ttf")
        font_prop = fm.FontProperties(fname=font_path)

        reshaped_labels = [get_display(arabic_reshaper.reshape(label)) for label in filenames]

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(reshaped_labels, durations, color='skyblue')
        ax.set_xlabel("مدت زمان (ثانیه)", fontproperties=font_prop)
        ax.set_title("مدت زمان فایل‌های ویدیویی", fontproperties=font_prop)

        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)
        for label in ax.get_yticklabels():
            label.set_fontproperties(font_prop)

        plt.tight_layout()
        plt.show()


# .......................................................................................


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # from PySide6.QtCore import Qt
    # app.setLayoutDirection(Qt.RightToLeft)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
