# video_worker.py
from PySide6.QtCore import QThread, Signal
import os

# import ffmpeg
from moviepy import VideoFileClip


class VideoWorker(QThread):
    progress = Signal(int)
    result = Signal(list)
    finished = Signal()
    error = Signal(str)

    def __init__(self, files):
        super().__init__()
        self.files = files
        self._is_running = True

    # def get_video_duration_ffmpeg(path):
    #     try:
    #         probe = ffmpeg.probe(path)
    #         duration = float(probe['format']['duration'])
    #         return duration
    #     except Exception as e:
    #         print(f"ffprobe error for {path}: {e}")
    #         return 0

    def stop(self):
        self._is_running = False

    def run(self):
        results = []
        total = len(self.files)

        for i, file in enumerate(self.files, 1):
            if not self._is_running:
                break

            # try:
            #     clip = VideoFileClip(file)
            #     duration = clip.duration
            #     clip.close()
            #     # duration = self.get_video_duration_ffmpeg(file)
            #
            #     results.append((os.path.basename(file), duration))
            # except Exception as e:
            #     self.error.emit(f"Error in '{file}': {str(e)}")
            #     results.append((os.path.basename(file), 0))

            clip = None
            try:
                clip = VideoFileClip(file)
                duration = clip.duration
                # duration = self.get_video_duration_ffmpeg(file)

            except Exception as e:
                duration = 0
                self.error.emit(f"Error in '{file}': {str(e)}")
            finally:
                results.append((os.path.basename(file), duration))

                if clip:
                    clip.close()

            self.progress.emit(i)

        self.result.emit(results)
        self.finished.emit()
