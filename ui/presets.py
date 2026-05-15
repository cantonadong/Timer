from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QDialog, QDialogButtonBox, QLineEdit, QFormLayout,
    QTimeEdit, QSizePolicy,
)
from PyQt5.QtCore import pyqtSignal, Qt, QTime, QSize, QTimer

from core.settings import PresetsManager
from ui.styles import (
    TEXT_PRIMARY, TEXT_TERTIARY, ACCENT, ACCENT_DARK,
    BG_CARD, SEPARATOR, BTN_RADIUS,
    CARD_STYLE, DIALOG_STYLE, make_shadow,
)

MAX_PRESETS = 3

_BTN_NORMAL = (
    f"QPushButton {{"
    f"  background-color: {BG_CARD};"
    f"  color: {TEXT_PRIMARY};"
    f"  border: 1.5px solid {SEPARATOR};"
    f"  border-radius: {BTN_RADIUS}px;"
    f"  font-size: 13px;"
    f"  font-weight: 500;"
    f"  padding: 5px 4px;"
    f"}}"
)
_BTN_HOVER = (
    f"QPushButton {{"
    f"  background-color: #EBF3FF;"
    f"  color: {ACCENT};"
    f"  border: 1.5px solid {ACCENT};"
    f"  border-radius: {BTN_RADIUS}px;"
    f"  font-size: 13px;"
    f"  font-weight: 500;"
    f"  padding: 5px 4px;"
    f"}}"
)


class PresetChip(QWidget):
    """Preset button with a subtle × that appears on hover and keeps the button in hover state."""

    clicked    = pyqtSignal()
    delete_req = pyqtSignal()

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(36)

        # Main label button
        self._btn = QPushButton(label, self)
        self._btn.setStyleSheet(_BTN_NORMAL)
        self._btn.clicked.connect(self.clicked)
        # Disable Qt's built-in hover so we control it ourselves
        self._btn.setAttribute(Qt.WA_Hover, False)

        # Delete × button — 16×16 circle, right-center
        self._del = QPushButton("✕", self)
        self._del.setFixedSize(QSize(16, 16))
        self._del.setCursor(Qt.PointingHandCursor)
        self._del.setStyleSheet(
            "QPushButton {"
            "  background: rgba(255,59,48,0.75);"
            "  color: white;"
            "  border: none;"
            "  border-radius: 8px;"
            "  font-size: 10px;"
            "  font-weight: 800;"
            "  padding: 0;"
            "}"
            "QPushButton:hover {"
            "  background: #FF3B30;"
            "}"
        )
        self._del.hide()
        self._del.clicked.connect(self.delete_req)

        # Keep track to avoid redundant style updates
        self._hovered = False

    def resizeEvent(self, event):
        self._btn.setGeometry(0, 0, self.width(), self.height())
        # Position × inside chip, right-center
        self._del.move(self.width() - 22, (self.height() - 16) // 2)

    def enterEvent(self, event):
        self._set_hovered(True)

    def leaveEvent(self, event):
        # Zero-delay check: by then any child enterEvent has fired
        QTimer.singleShot(0, self._check_leave)

    def _check_leave(self):
        if not self.underMouse():
            self._set_hovered(False)

    def _set_hovered(self, hovered: bool):
        if hovered == self._hovered:
            return
        self._hovered = hovered
        self._btn.setStyleSheet(_BTN_HOVER if hovered else _BTN_NORMAL)
        if hovered:
            self._del.show()
            self._del.raise_()
        else:
            self._del.hide()


class PresetBar(QWidget):
    preset_selected = pyqtSignal(int)  # seconds
    preset_deleted  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = PresetsManager()
        self._presets = []

        self.setObjectName("presetCard")
        self.setStyleSheet(f"QWidget#presetCard {{ {CARD_STYLE} }}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(0)

        # Header: title only
        self._header_lbl = QLabel("QUICK PRESETS")
        self._header_lbl.setStyleSheet(
            f"color: {TEXT_TERTIARY}; font-size: 10px; font-weight: 700;"
            " letter-spacing: 1px; background: transparent;"
        )
        outer.addWidget(self._header_lbl)
        outer.addSpacing(8)

        # Button row: chips expand equally
        self._btn_row = QHBoxLayout()
        self._btn_row.setSpacing(8)
        outer.addLayout(self._btn_row)

        make_shadow(self)
        self.rebuild()

    def rebuild(self):
        while self._btn_row.count():
            item = self._btn_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._presets = self._manager.load()[:MAX_PRESETS]

        for i, preset in enumerate(self._presets):
            chip = PresetChip(preset["label"])
            chip.clicked.connect(
                lambda s=preset["seconds"]: self.preset_selected.emit(s)
            )
            chip.delete_req.connect(lambda idx=i: self._delete_preset(idx))
            self._btn_row.addWidget(chip)

    def add_quick(self, label: str, seconds: int):
        """Save current countdown as a new preset (no dialog). Ignores duplicate durations."""
        if len(self._presets) >= MAX_PRESETS:
            return
        if any(p["seconds"] == seconds for p in self._presets):
            return
        self._manager.add(label, seconds)
        self.rebuild()

    def _delete_preset(self, index):
        self._manager.delete(index)
        self.rebuild()
        self.preset_deleted.emit()
