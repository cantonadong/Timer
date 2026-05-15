import os

from PyQt5.QtCore import QObject, pyqtSignal


class AudioPlayer(QObject):
    """Plays an MP3 file a fixed number of times; emits finished when done."""

    finished = pyqtSignal()

    def __init__(self, file_path: str, plays: int = 3, parent=None):
        super().__init__(parent)
        self._path = os.path.abspath(file_path)
        self._plays = plays
        self._count = 0
        self._player = None

        try:
            from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
            from PyQt5.QtCore import QUrl
            self._player = QMediaPlayer()
            self._player.setMedia(QMediaContent(QUrl.fromLocalFile(self._path)))
            self._player.mediaStatusChanged.connect(self._on_status)
        except Exception:
            self._player = None

    @property
    def available(self) -> bool:
        return self._player is not None and os.path.exists(self._path)

    def play(self):
        if not self.available:
            return
        self._count = 0
        self._player.setPosition(0)
        self._player.play()

    def stop(self):
        if self._player:
            self._player.stop()

    def _on_status(self, status):
        try:
            from PyQt5.QtMultimedia import QMediaPlayer
            if status == QMediaPlayer.EndOfMedia:
                self._count += 1
                if self._count < self._plays:
                    self._player.setPosition(0)
                    self._player.play()
                else:
                    self.finished.emit()
        except Exception:
            pass
