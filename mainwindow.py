# mainwindow.py
import os
import sys
from tabnanny import process_tokens

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem
)

from ui_mainwindow import Ui_MainWindow

from moviepy import VideoFileClip
# from moviepy.editor import VideoFileClip          # ERROR

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

        self.remaining_files = []  # فایلهای پردازش نشده
        self.results = []

        self.set_process_widgets_enable()

        # اتصال دکمه ها
        self.ui.btnSelectPath.clicked.connect(self.select_path)
        self.ui.btnSelectFiles.clicked.connect(self.select_files)
        self.ui.btnSaveToFile.clicked.connect(self.save_to_file)
        self.ui.btnChart.clicked.connect(self.show_chart)

        self.ui.btnPauseProcess.clicked.connect(self.pause_worker)
        self.ui.btnCancelProcess.clicked.connect(self.cancel_worker)
        self.ui.btnResumeProcess.clicked.connect(self.resume_worker)

        self.worker = None

        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Vazir.ttf")
        if os.path.exists(font_path):
            rcParams['font.family'] = 'Vazir'
            plt.rcParams['font.family'] = 'Vazir'

    # .......................................................................................

    def select_path(self):
        # نمایش دیالوگ انتخاب پوشه
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not path:
            return  # هیچ چیزی انتخاب نشد

        self.ui.statusbar.showMessage(path)

        include_subfolders = self.ui.chkSubfolders.isChecked()
        file_list = self.get_video_files(path, include_subfolders)

        # بررسی وجود فایل ویدئویی در پوشه انتخاب شده
        if file_list:
            self.start_worker(file_list)

    # .......................................................................................

    def select_files(self):

        path, _ = QFileDialog.getOpenFileNames(
            self, "Select Video File(s)", "", "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv)"
        )

        if not path:
            return  # هیچ چیزی انتخاب نشد
        else:
            self.ui.statusbar.showMessage(os.path.dirname(path[0]))

            # self.process_video(path[0])
            # file_list = self.get_video_files(path)
            file_list = path
            self.start_worker(file_list)

    # .......................................................................................

    def set_buttons_enable(self, is_enable=True):
        self.ui.btnSelectFiles.setEnabled(is_enable)
        self.ui.btnSelectPath.setEnabled(is_enable)
        self.ui.btnChart.setEnabled(is_enable)
        self.ui.btnSaveToFile.setEnabled(is_enable)

    # .......................................................................................

    def set_process_widgets_enable(self, btn_cancel_process=False, btn_pause_process=False,
                                   btn_resume_process=False, progressbar=False):
        self.ui.btnCancelProcess.setVisible(btn_cancel_process)
        self.ui.btnPauseProcess.setVisible(btn_pause_process)
        self.ui.btnResumeProcess.setVisible(btn_resume_process)
        self.ui.progressBar.setVisible(progressbar)

    # .......................................................................................

    def pause_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()

            # محاسبه فایل‌های باقی‌مانده
            self.remaining_files = self.worker.files[self.worker.current_index:]

            self.set_process_widgets_enable(btn_cancel_process=True, btn_pause_process=False,
                                            btn_resume_process=True, progressbar=True)

    def resume_worker(self):
        if self.remaining_files:
            self.start_worker(self.remaining_files)
            self.remaining_files = []

            self.set_process_widgets_enable(btn_cancel_process=True, btn_pause_process=True,
                                            btn_resume_process=False, progressbar=True)

    def cancel_worker(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.remaining_files = []
            # ...
            self.set_process_widgets_enable(False)

    # .......................................................................................

    @staticmethod
    def get_video_files_DEPRECATED(path):
        if os.path.isfile(path):
            return [path]

        video_ext = ['.mp4', '.avi', '.mkv', '.wmv', '.mov']
        return [os.path.join(path, f) for f in os.listdir(path) if os.path.splitext(f)[1].lower() in video_ext]

    @staticmethod
    def get_video_files(path, include_subfolders, ignore_errors=True):
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

            if include_subfolders:
                # استفاده از os.walk برای پیمایش بازگشتی
                for root, _, files in os.walk(path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in video_ext:
                            video_files.append(os.path.join(root, file))
            else:
                # فقط فایل‌های موجود در پوشه اصلی
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)

                    if os.path.islink(full_path):
                        continue

                    if os.path.isfile(full_path):
                        ext = os.path.splitext(entry)[1].lower()
                        if ext in video_ext:
                            video_files.append(full_path)

            return video_files

        except Exception as e:
            if not ignore_errors:
                raise
            print(f"خطا در پردازش مسیر '{path}': {str(e)}")
            return []

    # .......................................................................................

    # FIXME: [***] on resume, its not work well
    def start_worker(self, file_list):
        self.set_buttons_enable(False)
        self.set_process_widgets_enable(btn_cancel_process=True, btn_pause_process=True,
                                        btn_resume_process=False, progressbar=True)

        self.ui.tableFiles.setRowCount(0)

        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setMaximum(len(file_list))

        self.worker = VideoWorker(file_list)
        self.worker.progress.connect(self.ui.progressBar.setValue)
        self.worker.result.connect(self.populate_table)
        self.worker.finished.connect(lambda: self.set_buttons_enable(True))
        # self.worker.finished.connect(self.show_chart)
        self.worker.error.connect(self.show_error_message)

        self.worker.start()

    # .......................................................................................

    def populate_table(self, results):
        self.results = results
        self.ui.tableFiles.setRowCount(len(results))
        self.ui.tableFiles.setColumnCount(2)
        self.ui.tableFiles.setHorizontalHeaderLabels(["File Name", "Duration"])

        for i, (name, duration) in enumerate(results):
            self.ui.tableFiles.setItem(i, 0, QTableWidgetItem(name))
            self.ui.tableFiles.setItem(i, 1, QTableWidgetItem(f"{self.format_duration(duration)}"))

        self.ui.tableFiles.resizeColumnsToContents()

        # FIXME: ???
        # self.set_process_widgets_enable()
        # self.remaining_files = self.worker.files[self.worker.current_index:]

        self.set_buttons_enable()

    # .......................................................................................

    # TODO:
    def show_error_message(self, err_message):
        pass

    # .......................................................................................

    def process_video(self, file_path, show_result=True):
        duration = self.get_video_duration(file_path)

        if show_result:
            QMessageBox.information(self, "Video Duration",
                                    f"Video duration: {self.format_duration(duration)}")

    # .......................................................................................

    def get_video_duration(self, file_path):
        clip = None
        try:
            # خط زیر در کنسول اطلاعات را چاپ میکند!
            clip = VideoFileClip(file_path, )

            duration = clip.duration  # به ثانیه
            clip.close()
            return duration
        except Exception as e:
            if clip:
                clip.close()

            QMessageBox.critical(self, "Error", f"Failed to process: {file_path}\n{str(e)}")
            return 0

    # def get_video_duration_ffmpeg(path):
    #     try:
    #         probe = ffmpeg.probe(path)
    #         duration = float(probe['format']['duration'])
    #         return duration
    #     except Exception as e:
    #         print(f"ffprobe error for {path}: {e}")
    #         return 0

    # .......................................................................................

    @staticmethod
    def format_duration(seconds):
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02}:{mins:02}:{secs:02}"

    # .......................................................................................

    def save_to_file(self):
        if self.ui.tableFiles.rowCount() <= 0:
            QMessageBox.warning(self, "Err", "Table is empty!")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text File (*.txt);;CSV File (*.csv)")
        if not path:
            return

        try:
            with open(path, 'w', encoding='utf-8') as f:
                for row in range(self.ui.tableFiles.rowCount()):
                    filename = self.ui.tableFiles.item(row, 0).text()
                    duration = self.ui.tableFiles.item(row, 1).text()
                    f.write(f"{filename}, {duration}\n")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره‌سازی فایل:\n{str(e)}")

    # .......................................................................................

    # OK
    # TODO: چند تا باگ ریز در نمایش فونت فارسی داره
    def show_chart(self):
        filenames = []
        durations = []

        for row in range(self.ui.tableFiles.rowCount()):
            filenames.append(self.ui.tableFiles.item(row, 0).text())
            duration_text = self.ui.tableFiles.item(row, 1).text()
            h, m, s = map(int, duration_text.split(':'))
            total_seconds = h * 3600 + m * 60 + s
            durations.append(total_seconds)

        # مسیر فونت فارسی
        # font_path = os.path.join(os.path.dirname(__file__), "Vazir.ttf")
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Vazir.ttf")
        font_prop = fm.FontProperties(fname=font_path)

        # اصلاح نمایش فارسی
        reshaped_labels = [
            get_display(arabic_reshaper.reshape(label))
            # get_display(arabic_reshaper.reshape(os.path.basename(label)))  # اگر اسم فایل طولانی باشد، ممکن است در نموار خوب نشان داده نشود. این کد اصلاح میکند این نقیص را
            for label in filenames
        ]

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
