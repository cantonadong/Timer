from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont

from core.timer_engine import TimerMode
from ui.styles import ACCENT, BG_TOGGLE, TEXT_TERTIARY, BTN_RADIUS

_INSET = 3
_RADIUS = BTN_RADIUS - 2

# Tab order: Countdown first (index 0), Count Up second (index 1)
_LABELS = ["Countdown", "Count Up"]
_MODES  = [TimerMode.COUNTDOWN, TimerMode.COUNTUP]


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

        self.setFixedSize(240, 40)
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
        # Countdown → left (index 0), Count Up → right (index 1)
        return float(_INSET) if mode == TimerMode.COUNTDOWN else self.width() / 2.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = float(self.width()), float(self.height())
        half = w / 2.0

        # Container
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(BG_TOGGLE))
        painter.drawRoundedRect(QRectF(0, 0, w, h), BTN_RADIUS, BTN_RADIUS)

        # Indicator
        ind_w = half - float(_INSET)
        ind_h = h - 2 * _INSET
        painter.setBrush(QColor(ACCENT))
        painter.drawRoundedRect(
            QRectF(self._indicator_x, _INSET, ind_w, ind_h), _RADIUS, _RADIUS
        )

        # Labels
        font = QFont("Segoe UI")
        font.setPointSize(13)
        font.setWeight(QFont.Medium)
        painter.setFont(font)

        for i, (label, mode) in enumerate(zip(_LABELS, _MODES)):
            rect = QRectF(i * half, 0.0, half, h)
            painter.setPen(
                QColor("white") if self._mode == mode else QColor(TEXT_TERTIARY)
            )
            painter.drawText(rect, Qt.AlignCenter, label)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        idx = 0 if event.x() < self.width() // 2 else 1
        new_mode = _MODES[idx]
        if new_mode == self._mode:
            return
        self._mode = new_mode
        self._anim.setStartValue(self._indicator_x)
        self._anim.setEndValue(self._target_x(new_mode))
        self._anim.start()
        self.update()
        self.mode_changed.emit(new_mode)
