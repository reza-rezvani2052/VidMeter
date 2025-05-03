# mainwindow.py

import os
import json
import re

from ui_mainwindow import Ui_MainWindow

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox, QMenu, QToolTip
)

from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, QUrl, QSettings
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# ...

# os.environ["QT_API"] = "pyside6"  # تنظیم متغیر محیطی
import matplotlib

matplotlib.use("QtAgg")  # انتخاب backend مناسب
# from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure

import matplotlib.pyplot as plt
# matplotlib.rcParams["backend.qt6"] = "PySide6"  # تنظیم wrapper به PySide6
import matplotlib.font_manager as fm
from matplotlib import rcParams

# ...

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

        self.audio_output = None
        self.media_player = None

        self.setup_ui()
        self.load_settings()

        # ...

        self.worker = None
        self.is_paused = False

        font_path = os.path.join(os.path.dirname(__file__), "fonts", "Vazir.ttf")
        if os.path.exists(font_path):
            rcParams['font.family'] = 'Vazir'
            plt.rcParams['font.family'] = 'Vazir'

    def setup_ui(self):
        self.setWindowTitle("VidMeter")
        self.setAcceptDrops(True)

        self.ui.video_widget.setFixedSize(300, 200)

        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.ui.video_widget)
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        self.ui.sliderSeek.setRange(0, 0)  # تا وقتی ویدیو لود بشه
        self.ui.sliderSeek.sliderMoved.connect(self.show_slider_tooltip)

        # موقع تغییر موقعیت ویدیو، اسلایدر بروزرسانی شه
        self.media_player.positionChanged.connect(self.update_slider_position)

        # وقتی طول ویدیو مشخص شد، رنج اسلایدر تنظیم بشه
        self.media_player.durationChanged.connect(self.set_slider_range)

        # وقتی کاربر اسلایدر رو تغییر بده، ویدیو seek بشه
        self.ui.sliderSeek.sliderMoved.connect(self.seek_video)

        self.ui.video_widget.clicked.connect(self.toggle_play_pause)
        self.ui.video_widget.doubleClicked.connect(self.toggle_fullscreen)

        # ...

        self.ui.tableFiles.installEventFilter(self)
        self.ui.tableFiles.setSortingEnabled(True)
        self.ui.tableFiles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableFiles.customContextMenuRequested.connect(self.show_table_context_menu)
        # self.ui.tableFiles.itemClicked.connect(self.preview_video)
        self.ui.tableFiles.itemDoubleClicked.connect(self.preview_video)
        self.ui.tableFiles.itemSelectionChanged.connect(self.update_selected_duration)

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

        self.ui.actSaveProject.triggered.connect(self.save_project)
        self.ui.actLoadProject.triggered.connect(self.load_project)
        self.ui.btnProject.addAction(self.ui.actSaveProject)
        self.ui.btnProject.addAction(self.ui.actLoadProject)

        self.ui.ledSearchInTableFiles.textChanged.connect(self.filter_table_files_rows)
        self.ui.btnClearSearch.clicked.connect(self.clear_search)
        self.ui.comboSearchColumn.currentIndexChanged.connect(self.filter_table_files_rows)
        self.ui.ledSearchInTableFiles.setToolTip(
            "🔍 فیلتر نام یا مدت‌زمان\n"
            "مثال‌ها:\n"
            "  ویدیو           ← جستجو در نام یا زمان\n"
            "  00:10           ← تطابق با زمان 10 ثانیه\n"
            "  >01:00:00       ← بیشتر از 1 ساعت\n"
            "  <=05:30         ← کمتر یا مساوی 5 دقیقه و 30 ثانیه\n"
        )

    def eventFilter(self, source, event):
        if source == self.ui.tableFiles and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key_Delete:
                self.delete_selected_rows()
                return True  # رویداد پردازش شد

        return super().eventFilter(source, event)

    def select_path(self):
        last_path = self.ui.lineEditFolder.text().strip()
        if not os.path.exists(last_path):
            last_path = "."
        path = QFileDialog.getExistingDirectory(self, "Select Folder",
                                                last_path)
        if not path:
            return

        self.ui.statusbar.showMessage(path)
        self.ui.lineEditFolder.setText(path)

        file_list = self.get_video_files(path, check_subfolders=self.ui.chkSubfolder.isChecked())
        if file_list:
            self.start_worker(file_list)

    def select_files(self):
        last_path = self.ui.lineEditFolder.text().strip()
        if not os.path.exists(last_path):
            last_path = "."

        path, _ = QFileDialog.getOpenFileNames(
            self, "Select Video File(s)", last_path, "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv)"
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
        self.ui.btnProject.setEnabled(is_enable)

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
        self.set_buttons_enable(True)
        # ...
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
            item_name = QTableWidgetItem(name)
            item_name.setData(Qt.UserRole, name)
            # item_name.setData(Qt.UserRole,path)   #TODO:

            item_duration = QTableWidgetItem(f"{self.format_duration(duration)}")

            if duration == 0:
                item_name.setForeground(Qt.red)
                item_duration.setForeground(Qt.red)

            self.ui.tableFiles.setItem(i, 0, item_name)
            self.ui.tableFiles.setItem(i, 1, item_duration)

        self.ui.tableFiles.resizeColumnsToContents()

        total_duration = self.calculate_total_duration()
        total_text = self.format_duration(total_duration)

        self.ui.statusbar.showMessage(f"مجموع مدت‌زمان همه ویدیوها: {total_text}")

    def show_table_context_menu(self, position):
        indexes = self.ui.tableFiles.selectedIndexes()

        if not indexes:
            return

        selected_rows = set(index.row() for index in indexes)

        menu = QMenu()
        # menu = QMenu(self)

        delete_action = menu.addAction("🗑 حذف سطر(ها)")
        copy_action = menu.addAction("📋 کپی به کلیپ‌بورد")
        save_action = menu.addAction("💾 ذخیره انتخاب‌شده‌ها به فایل")

        # فقط در صورتی که فقط یک سطر انتخاب شده باشد
        if len(selected_rows) == 1:
            detail_action = menu.addAction("ℹ نمایش جزئیات ویدیو")
        else:
            detail_action = None

        action = menu.exec(self.ui.tableFiles.viewport().mapToGlobal(position))

        if action == delete_action:
            self.delete_selected_rows()
        elif action == copy_action:
            self.copy_selected_to_clipboard()
        elif action == save_action:
            self.save_selected_to_file()
        elif detail_action and action == detail_action:
            self.show_video_details()

    @staticmethod
    def format_duration(seconds):
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02}:{mins:02}:{secs:02}"

    @staticmethod
    def duration_to_seconds(duration_str):
        try:
            parts = list(map(int, duration_str.split(':')))
            while len(parts) < 3:
                parts.insert(0, 0)  # تبدیل 05:30 به 00:05:30
            h, m, s = parts
            return h * 3600 + m * 60 + s
        except Exception:
            return -1

    def copy_selected_to_clipboard(self):
        selected = self.ui.tableFiles.selectedItems()
        if not selected:
            return

        rows = set(item.row() for item in selected)
        text = ""

        for row in sorted(rows):
            name = self.ui.tableFiles.item(row, 0).text()
            duration = self.ui.tableFiles.item(row, 1).text()
            text += f"{name}, {duration}\n"

        QApplication.clipboard().setText(text.strip())

    def save_selected_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Selected", "", "Text File (*.txt);;CSV File (*.csv)")
        if not path:
            return

        selected = self.ui.tableFiles.selectedItems()
        if not selected:
            return

        rows = set(item.row() for item in selected)

        with open(path, 'w', encoding='utf-8') as f:
            for row in sorted(rows):
                name = self.ui.tableFiles.item(row, 0).text()
                duration = self.ui.tableFiles.item(row, 1).text()
                f.write(f"{name}, {duration}\n")

    def save_to_file(self):
        if self.ui.tableFiles.rowCount() <= 0:
            QApplication.beep()
            self.ui.statusbar.showMessage("جدول خالی است", 3000)
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text File (*.txt);;CSV File (*.csv)")
        if not path:
            return

        with open(path, 'w', encoding='utf-8') as f:
            for row in range(self.ui.tableFiles.rowCount()):
                filename = self.ui.tableFiles.item(row, 0).text()
                duration = self.ui.tableFiles.item(row, 1).text()
                f.write(f"{filename}, {duration}\n")

    def show_chart(self):
        if self.ui.tableFiles.rowCount() <= 0:
            QApplication.beep()
            self.ui.statusbar.showMessage("جدول خالی است", 3000)
            return

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

    def save_project(self):
        if self.ui.tableFiles.rowCount() <= 0:
            QApplication.beep()
            self.ui.statusbar.showMessage("جدول خالی است", 3000)
            return

        path, _ = QFileDialog.getSaveFileName(self, "ذخیره پروژه", "", "Project Files (*.json)")
        if not path:
            return

        data = []
        for row in range(self.ui.tableFiles.rowCount()):
            name_item = self.ui.tableFiles.item(row, 0)
            duration_item = self.ui.tableFiles.item(row, 1)

            filepath = name_item.data(Qt.UserRole)
            duration_str = duration_item.text()

            # تبدیل hh:mm:ss به ثانیه
            try:
                h, m, s = map(int, duration_str.split(":"))
                duration_sec = h * 3600 + m * 60 + s
            except ValueError:
                duration_sec = 0

            data.append({
                "filename": name_item.text(),
                "filepath": filepath,
                "duration": duration_sec
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.statusBar().showMessage(f"✅ پروژه ذخیره شد: {path}")

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "باز کردن پروژه", "", "Project Files (*.json)")
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در خواندن فایل:\n{e}")
            return

        self.ui.tableFiles.setRowCount(0)

        for entry in data:
            row = self.ui.tableFiles.rowCount()
            self.ui.tableFiles.insertRow(row)

            item_name = QTableWidgetItem(entry["filename"])
            item_name.setData(Qt.UserRole, entry["filepath"])

            # تبدیل ثانیه به hh:mm:ss
            total_seconds = int(entry["duration"])
            item_duration = QTableWidgetItem(f"{self.format_duration(total_seconds)}")

            if total_seconds == 0:
                item_name.setForeground(Qt.red)
                item_duration.setForeground(Qt.red)

            self.ui.tableFiles.setItem(row, 0, item_name)
            self.ui.tableFiles.setItem(row, 1, item_duration)

        self.ui.tableFiles.resizeColumnsToContents()
        self.statusBar().showMessage(f"📂 پروژه بارگذاری شد: {path}")

    def clear_search(self):
        self.ui.ledSearchInTableFiles.clear()
        self.ui.comboSearchColumn.setCurrentIndex(0)

    def filter_table_files_rows(self, text):
        text = self.ui.ledSearchInTableFiles.text().strip()
        column = self.ui.comboSearchColumn.currentText()

        for row in range(self.ui.tableFiles.rowCount()):
            name = self.ui.tableFiles.item(row, 0).text().lower()
            duration_str = self.ui.tableFiles.item(row, 1).text().lower()
            row_sec = self.duration_to_seconds(duration_str)

            show_row = False

            # بررسی فیلتر شرطی (فقط روی مدت‌زمان)
            match = re.match(r'^(>=|<=|>|<|=)?\s*(\d+:\d+:\d+|\d+:\d+|\d+)$', text)
            is_conditional = match is not None

            if column == "All Columns":
                if is_conditional:
                    operator, time_str = match.groups()
                    filter_sec = self.duration_to_seconds(time_str)

                    if operator == '>' and row_sec > filter_sec:
                        show_row = True
                    elif operator == '>=' and row_sec >= filter_sec:
                        show_row = True
                    elif operator == '<' and row_sec < filter_sec:
                        show_row = True
                    elif operator == '<=' and row_sec <= filter_sec:
                        show_row = True
                    elif operator == '=' or operator is None:
                        show_row = abs(row_sec - filter_sec) <= 1
                else:
                    show_row = text.lower() in name or text.lower() in duration_str

            elif column == "File Name":
                show_row = text.lower() in name

            elif column == "Duration":
                if is_conditional:
                    operator, time_str = match.groups()
                    filter_sec = self.duration_to_seconds(time_str)

                    if operator == '>' and row_sec > filter_sec:
                        show_row = True
                    elif operator == '>=' and row_sec >= filter_sec:
                        show_row = True
                    elif operator == '<' and row_sec < filter_sec:
                        show_row = True
                    elif operator == '<=' and row_sec <= filter_sec:
                        show_row = True
                    elif operator == '=' or operator is None:
                        show_row = abs(row_sec - filter_sec) <= 1
                else:
                    show_row = text.lower() in duration_str

            self.ui.tableFiles.setRowHidden(row, not show_row)

    # ..........................................................................

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.load_files(paths)

    # ..........................................................................

    def show_slider_tooltip(self, position):
        # تبدیل میلی‌ثانیه به hh:mm:ss
        seconds = position // 1000
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        time_str = f"{h:02}:{m:02}:{s:02}"

        # نمایش tooltip در محل موس
        from PySide6.QtGui import QCursor
        QToolTip.showText(QCursor.pos(), time_str, self.ui.sliderSeek)

    def set_slider_range(self, duration):
        self.ui.sliderSeek.setRange(0, duration)

    def update_slider_position(self, position):
        self.ui.sliderSeek.setValue(position)

    def seek_video(self, position):
        self.media_player.setPosition(position)

    # ..........................................................................

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def toggle_fullscreen(self):
        if self.ui.video_widget.isFullScreen():
            self.ui.video_widget.setFullScreen(False)
        else:
            self.ui.video_widget.setFullScreen(True)
            self.ui.video_widget.setFocus()  # گرفتن فوکوس برای دریافت key

    def adjust_volume(self, step_percent):
        volume = self.audio_output.volume() * 100
        volume = max(0, min(100, volume + step_percent))
        self.audio_output.setVolume(volume / 100.0)
        self.statusBar().showMessage(f"🎧 Volume: {int(volume)}%")

    def toggle_mute(self):
        is_muted = self.audio_output.isMuted()
        self.audio_output.setMuted(not is_muted)
        msg = "🔇 Muted" if not is_muted else "🔊 Unmuted"
        self.statusBar().showMessage(msg)

    # def seek_relative(self, offset_ms):
    #     current_pos = self.media_player.position()
    #     new_pos = max(0, current_pos + offset_ms)
    #     self.media_player.setPosition(new_pos)
    def seek_relative(self, offset_ms):
        new_pos = max(0, self.media_player.position() + offset_ms)
        self.media_player.setPosition(new_pos)

    def preview_video(self):
        items = self.ui.tableFiles.selectedItems()
        if not items:
            return
        row = items[0].row()
        filename_item = self.ui.tableFiles.item(row, 0)
        filepath = filename_item.data(Qt.UserRole)
        # print(filepath)   #TODO:
        # if filepath and os.path.exists(filepath):
        #     self.media_player.setSource(QUrl.fromLocalFile(filepath))
        #     self.media_player.play()

        # TODO:
        if filename_item and os.path.exists(filename_item.text()):
            self.media_player.setSource(QUrl.fromLocalFile(filename_item.text()))
            self.media_player.play()

        # Test:
        # self.media_player.setSource(QUrl.fromLocalFile("C:\\Users\\Hossein\\Desktop\\lesson_22.mp4"))
        # self.media_player.play()

    # ..........................................................................

    def delete_selected_rows(self):
        rows = sorted(set(index.row() for index in self.ui.tableFiles.selectedIndexes()), reverse=True)
        for row in rows:
            self.ui.tableFiles.removeRow(row)

    # ..........................................................................

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        selected_rows = sorted(set(index.row() for index in self.ui.tableFiles.selectedIndexes()))
        data = []
        for row in selected_rows:
            row_data = []
            for col in range(self.ui.tableFiles.columnCount()):
                item = self.ui.tableFiles.item(row, col)
                row_data.append(item.text() if item else '')
            data.append("\t".join(row_data))
        clipboard.setText("\n".join(data))

    # ..........................................................................

    def show_video_details(self):
        selected = self.ui.tableFiles.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        filename = self.ui.tableFiles.item(row, 0).text()
        duration = self.ui.tableFiles.item(row, 1).text()
        QMessageBox.information(self,
                                "جزئیات ویدیو",
                                f"🖹 نام فایل: {filename}\n⏱ مدت زمان: {duration}"
                                )

    # ..........................................................................

    def load_settings(self):
        settings = QSettings("VidMeter", "Settings")
        last_folder = settings.value("last_folder", "")
        if last_folder:
            self.ui.lineEditFolder.setText(last_folder)
        self.restoreGeometry(settings.value("geometry", b""))
        self.restoreState(settings.value("window_state", b""))

        include_subfolders = settings.value("subfolder", True, type=bool)
        self.ui.chkSubfolder.setChecked(include_subfolders)

    def save_settings(self):
        settings = QSettings("VidMeter", "Settings")
        settings.setValue("last_folder", self.ui.lineEditFolder.text())
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())
        settings.setValue("subfolder", self.ui.chkSubfolder.isChecked())

    # ..........................................................................

    def load_files(self, paths):
        file_list = []
        check_subfolders = self.ui.chkSubfolder.isChecked()

        for path in paths:

            if os.path.isdir(path):
                if check_subfolders:
                    # جستجوی بازگشتی در تمام زیرپوشه‌ها
                    for root, _, files in os.walk(path):
                        for f in files:
                            if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                                file_list.append(os.path.join(root, f))
                else:
                    # فقط فایل‌های موجود در همان پوشه
                    for f in os.listdir(path):
                        full_path = os.path.join(path, f)
                        if os.path.isfile(full_path) and f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                            file_list.append(full_path)

            elif os.path.isfile(path) and path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                file_list.append(path)

        if file_list:
            self.start_worker(file_list)

    # ..........................................................................

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)
