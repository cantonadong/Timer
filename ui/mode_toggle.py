from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont

from core.timer_engine import TimerMode
from ui.styles import ACCENT, BG_TOGGLE, TEXT_TERTIARY, BTN_RADIUS

_INSET = 3
_RADIUS = BTN_RADIUS - 2
_SEGMENT_W = 126

# Tab order: Countdown, Count Up, Reminder
_LABELS = ["Countdown", "Count Up", "Reminder"]
_MODES  = [TimerMode.COUNTDOWN, TimerMode.COUNTUP, TimerMode.REMINDER]


class ModeToggle(QWidget):
    mode_changed = pyqtSignal(object)  # TimerMode — only on user click

    def __init__(self, parent=None):
        super().__init__(parent)
        # Default: Countdown (left side, index 0)
        self._mode = TimerMode.COUNTDOWN
        self._indicator_x = float(_INSET)

        self._anim = QPropertyAnimation(self, b"indicator_x")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self.setFixedSize(_SEGMENT_W * len(_MODES), 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground, False)

    def _get_indicator_x(self):
        return self._indicator_x

    def _set_indicator_x(self, val):
        self._indicator_x = val
        self.update()

    indicator_x = pyqtProperty(float, _get_indicator_x, _set_indicator_x)

    @property
    def mode(self):
        return self._mode

    def set_mode(self, mode, animate=True):
        """Programmatic change — does NOT emit mode_changed."""
        if mode == self._mode:
            return
        self._mode = mode
        target = self._target_x(mode)
        if animate:
            self._anim.setStartValue(self._indicator_x)
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self._indicator_x = target
            self.update()

    def _target_x(self, mode):
        # First segment sits flush against the inset; each later segment starts
        # at its own multiple of the segment width (see paintEvent for why this
        # keeps a matching inset gap on the right edge for the last segment).
        idx = _MODES.index(mode)
        seg_w = self.width() / len(_MODES)
        return float(_INSET) if idx == 0 else idx * seg_w

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(1.0 if self.isEnabled() else 0.4)

        w, h = float(self.width()), float(self.height())
        seg_w = w / len(_MODES)

        # Container
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(BG_TOGGLE))
        painter.drawRoundedRect(QRectF(0, 0, w, h), BTN_RADIUS, BTN_RADIUS)

        # Indicator
        ind_w = seg_w - float(_INSET)
        ind_h = h - 2 * _INSET
        painter.setBrush(QColor(ACCENT))
        painter.drawRoundedRect(
            QRectF(self._indicator_x, _INSET, ind_w, ind_h), _RADIUS, _RADIUS
        )

        # Labels
        font = QFont("Segoe UI")
        font.setPointSize(11)
        font.setWeight(QFont.Medium)
        painter.setFont(font)

        for i, (label, mode) in enumerate(zip(_LABELS, _MODES)):
            rect = QRectF(i * seg_w, 0.0, seg_w, h)
            painter.setPen(
                QColor("white") if self._mode == mode else QColor(TEXT_TERTIARY)
            )
            painter.drawText(rect, Qt.AlignCenter, label)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        seg_w = self.width() / len(_MODES)
        idx = min(len(_MODES) - 1, int(event.x() // seg_w))
        new_mode = _MODES[idx]
        if new_mode == self._mode:
            return
        self._mode = new_mode
        self._anim.setStartValue(self._indicator_x)
        self._anim.setEndValue(self._target_x(new_mode))
        self._anim.start()
        self.update()
        self.mode_changed.emit(new_mode)
