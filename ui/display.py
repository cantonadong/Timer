from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics

from ui.styles import TEXT_PRIMARY, DANGER


class TimeDisplay(QWidget):
    """Large time display — fixed-width digit cells, scroll-adjustable in countdown mode."""

    scroll_segment = pyqtSignal(str, int)  # ('h'|'m'|'s', +1|-1)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._time_str = "00:00:00"
        self._color = TEXT_PRIMARY
        self._scroll_enabled = False
        self._seg_h_end = 0.0
        self._seg_m_end = 0.0
        self._flash_timer = None
        self._flash_count = 0

        self._font = QFont("Segoe UI")
        self._font.setPointSize(60)
        self._font.setWeight(QFont.Light)

        self.setMinimumHeight(105)
        self.setAttribute(Qt.WA_StyledBackground, False)

    # ── Public API ─────────────────────────────────────────────────────────

    def set_time_ms(self, ms):
        total_s = max(0, int(ms)) // 1000
        h, m, s = total_s // 3600, (total_s % 3600) // 60, total_s % 60
        new = f"{h:02d}:{m:02d}:{s:02d}"
        if new != self._time_str:
            self._time_str = new
            self.update()

    def set_scroll_enabled(self, enabled: bool):
        self._scroll_enabled = enabled
        self.setCursor(Qt.SizeVerCursor if enabled else Qt.ArrowCursor)

    def start_flash(self):
        self.stop_flash()
        self._flash_count = 0
        self._flash_timer = QTimer(self)
        self._flash_timer.setInterval(280)
        self._flash_timer.timeout.connect(self._do_flash)
        self._flash_timer.start()

    def stop_flash(self):
        if self._flash_timer is not None:
            self._flash_timer.stop()
            self._flash_timer.deleteLater()
            self._flash_timer = None
        self._color = TEXT_PRIMARY
        self.update()

    # ── Paint ──────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(self._font)

        fm = QFontMetrics(self._font)
        cell_w = max(fm.horizontalAdvance(str(d)) for d in range(10))
        colon_w = fm.horizontalAdvance(":")

        total_w = 6.0 * cell_w + 2.0 * colon_w
        start_x = (self.width() - total_w) / 2.0
        baseline = self.height() / 2.0 + (fm.ascent() - fm.descent()) / 2.0

        # Segment boundaries (midpoint of each colon)
        self._seg_h_end = start_x + 2.0 * cell_w + colon_w * 0.5
        self._seg_m_end = start_x + 4.0 * cell_w + colon_w * 1.5

        # Time digits — each in a fixed-width cell
        painter.setPen(QColor(self._color))
        x = start_x
        for ch in self._time_str:
            if ch == ":":
                painter.drawText(QPointF(x, baseline), ch)
                x += colon_w
            else:
                ch_w = fm.horizontalAdvance(ch)
                painter.drawText(QPointF(x + (cell_w - ch_w) / 2.0, baseline), ch)
                x += cell_w

        painter.end()

    # ── Scroll ─────────────────────────────────────────────────────────────

    def wheelEvent(self, event):
        if not self._scroll_enabled:
            return
        delta = 1 if event.angleDelta().y() > 0 else -1
        x = float(event.pos().x())
        seg = "h" if x < self._seg_h_end else ("m" if x < self._seg_m_end else "s")
        self.scroll_segment.emit(seg, delta)
        event.accept()

    # ── Flash ──────────────────────────────────────────────────────────────

    def _do_flash(self):
        self._flash_count += 1
        self._color = DANGER if self._flash_count % 2 == 1 else TEXT_PRIMARY
        self.update()
