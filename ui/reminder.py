from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from ui.styles import (
    TEXT_TERTIARY, TEXT_SECONDARY, ACCENT,
    BG_CARD, SEPARATOR, GREEN_ACTIVE, CARD_STYLE, make_shadow,
)

OFFSET_OPTIONS = [5, 10, 15, 20, 30, 45, 60]   # minutes
_MIN_OFFSET, _MAX_OFFSET = 0, 180
_DEFAULT_ON_OFFSET = 5


class _OffsetChip(QPushButton):
    def __init__(self, minutes: int, parent=None):
        super().__init__(str(minutes), parent)
        self.minutes = minutes
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(24)
        self.toggled.connect(self._refresh)
        self._refresh(False)

    def _refresh(self, checked):
        if checked:
            self.setStyleSheet(
                f"QPushButton {{ background:{ACCENT}; color:white; border:none;"
                f" border-radius:6px; font-size:11px; font-weight:700; }}"
            )
        else:
            self.setStyleSheet(
                f"QPushButton {{ background:{BG_CARD}; color:{TEXT_SECONDARY};"
                f" border:1.5px solid {SEPARATOR}; border-radius:6px;"
                f" font-size:11px; font-weight:500; }}"
                f"QPushButton:hover {{ border-color:{ACCENT}; color:{ACCENT}; }}"
            )


class _SwitchBtn(QPushButton):
    """Compact Off/On pill — mirrors the title bar's 'Top' toggle chip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(20)
        self.toggled.connect(self._refresh)
        self._refresh(False)

    def sizeHint(self):
        return QSize(38, 20)

    def _refresh(self, on):
        if on:
            self.setText("On")
            self.setStyleSheet(
                f"QPushButton {{ background:{GREEN_ACTIVE}; color:white; border:none;"
                f" border-radius:6px; font-size:10px; font-weight:700; padding:0 8px; }}"
            )
        else:
            self.setText("Off")
            self.setStyleSheet(
                f"QPushButton {{ background:rgba(142,142,147,0.18); color:{TEXT_TERTIARY};"
                f" border:none; border-radius:6px; font-size:10px; font-weight:600; padding:0 8px; }}"
            )


class ReminderPanel(QWidget):
    """
    Advance-reminder selector for Reminder mode.

    Off by default — the alert fires exactly at the target time. Switching it
    on lets the user pick one of the quick offsets, or fine-tune with the
    mouse wheel (any value from 0 up rounds back down to "off" at 0).
    """

    offset_changed = pyqtSignal(int)  # minutes; 0 == off / on-time

    def __init__(self, parent=None):
        super().__init__(parent)
        self._offset = 0
        self._last_on_offset = _DEFAULT_ON_OFFSET

        self.setObjectName("reminderCard")
        self.setStyleSheet(f"QWidget#reminderCard {{ {CARD_STYLE} }}")
        self.setCursor(Qt.SizeVerCursor)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)
        title = QLabel("REMIND ME EARLY")
        title.setStyleSheet(
            f"color:{TEXT_TERTIARY}; font-size:10px; font-weight:700;"
            " letter-spacing:1px; background:transparent;"
        )
        self._value_lbl = QLabel()
        self._value_lbl.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:11px; font-weight:600; background:transparent;"
        )
        self._switch = _SwitchBtn()
        self._switch.toggled.connect(self._on_switch_toggled)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._value_lbl)
        header.addWidget(self._switch)
        outer.addLayout(header)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(6)
        self._chips = []
        for minutes in OFFSET_OPTIONS:
            chip = _OffsetChip(minutes)
            chip.clicked.connect(lambda _=False, m=minutes: self.set_offset(m))
            chip_row.addWidget(chip)
            self._chips.append(chip)
        outer.addLayout(chip_row)

        make_shadow(self)
        self._sync(notify=False)

    @property
    def offset_minutes(self) -> int:
        return self._offset

    def set_offset(self, minutes: int, notify=True):
        minutes = max(_MIN_OFFSET, min(_MAX_OFFSET, minutes))
        if minutes == self._offset:
            return
        self._offset = minutes
        if minutes > 0:
            self._last_on_offset = minutes
        self._sync(notify=notify)

    def _on_switch_toggled(self, on: bool):
        if on and self._offset == 0:
            self.set_offset(self._last_on_offset)
        elif not on and self._offset != 0:
            self.set_offset(0)

    def _sync(self, notify=True):
        # blockSignals() also suppresses the toggled->_refresh visual update,
        # so re-apply each widget's style explicitly after setChecked().
        on = self._offset > 0
        self._switch.blockSignals(True)
        self._switch.setChecked(on)
        self._switch.blockSignals(False)
        self._switch._refresh(on)
        self._value_lbl.setText(f"{self._offset} min" if on else "on time")
        for chip in self._chips:
            checked = chip.minutes == self._offset
            chip.blockSignals(True)
            chip.setChecked(checked)
            chip.blockSignals(False)
            chip._refresh(checked)
        if notify:
            self.offset_changed.emit(self._offset)

    def wheelEvent(self, event):
        delta = 1 if event.angleDelta().y() > 0 else -1
        self.set_offset(self._offset + delta)
        event.accept()
