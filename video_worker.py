# video_worker.py

import os
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition

# import ffmpeg
from moviepy import VideoFileClip
# from moviepy.editor import VideoFileClip          # ERROR


class VideoWorker(QThread):
    progress = Signal(int)
    result = Signal(list)
    finished = Signal()  # پایان کامل کار
    error = Signal(str)


    def __init__(self, files):
        super().__init__()
        self.files = files
        self._is_paused = False
        self._is_cancelled = False

        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()

    # ...
    """
    def get_video_duration_ffmpeg(path):
        try:
            probe = ffmpeg.probe(path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            print(f"ffprobe error for {path}: {e}")
            return 0
    """
    # ...

    def run(self):
        results = []
        # total = len(self.files)

        for i, file in enumerate(self.files, 1):
            # بررسی وضعیت pause
            self._mutex.lock()
            while self._is_paused:
                self._wait_condition.wait(self._mutex)
            self._mutex.unlock()

            # بررسی وضعیت cancel
            if self._is_cancelled:
                break

            try:
                clip = VideoFileClip(file)
                duration = clip.duration
                clip.close()

                # results.append((os.path.basename(file), duration)) #TODO: ***
                results.append((file, duration))
            except Exception as e:
                self.error.emit(os.path.basename(file))
                results.append((os.path.basename(file), 0))

            self.progress.emit(i)

        self.result.emit(results)
        self.finished.emit()

    def pause(self):
        self._mutex.lock()
        self._is_paused = True
        self._mutex.unlock()

    def resume(self):
        self._mutex.lock()
        self._is_paused = False
        self._mutex.unlock()
        self._wait_condition.wakeAll()

    def cancel(self):
        self._mutex.lock()
        self._is_cancelled = True
        self._is_paused = False  # برای اینکه اگر Pause بود، از wait خارج بشه
        self._mutex.unlock()
        self._wait_condition.wakeAll()
