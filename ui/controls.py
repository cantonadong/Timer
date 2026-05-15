from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal

from core.timer_engine import TimerState
from ui.styles import (
    PRIMARY_BTN_STYLE, PAUSE_BTN_STYLE, DANGER_BTN_STYLE,
    CARD_STYLE, make_shadow,
)

_BTN_H = 48


class ControlPanel(QWidget):
    """
    Combined Start / Pause / Resume button (label & color change with state) + Reset.
    """

    start_clicked  = pyqtSignal()
    pause_clicked  = pyqtSignal()
    resume_clicked = pyqtSignal()
    reset_clicked  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("controlCard")
        self.setStyleSheet(f"QWidget#controlCard {{ {CARD_STYLE} }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.btn_action = QPushButton("Start")
        self.btn_action.setFixedHeight(_BTN_H)
        self.btn_action.setStyleSheet(PRIMARY_BTN_STYLE)
        self.btn_action.clicked.connect(self._on_action)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedHeight(_BTN_H)
        self.btn_reset.setStyleSheet(DANGER_BTN_STYLE)
        self.btn_reset.clicked.connect(self.reset_clicked)

        layout.addWidget(self.btn_action)
        layout.addWidget(self.btn_reset)

        make_shadow(self)
        self._state = TimerState.IDLE
        self._apply(TimerState.IDLE)

    def _on_action(self):
        if self._state == TimerState.IDLE:
            self.start_clicked.emit()
        elif self._state == TimerState.RUNNING:
            self.pause_clicked.emit()
        elif self._state == TimerState.PAUSED:
            self.resume_clicked.emit()

    def update_state(self, state):
        self._state = state
        self._apply(state)

    def set_start_enabled(self, enabled: bool):
        """Enable or disable the start button (only meaningful in IDLE state)."""
        if self._state == TimerState.IDLE:
            self.btn_action.setEnabled(enabled)

    def _apply(self, state):
        # Reset is always enabled; action button defaults to enabled (caller may override)
        self.btn_reset.setEnabled(True)
        self.btn_action.setEnabled(True)
        if state == TimerState.IDLE:
            self.btn_action.setText("Start")
            self.btn_action.setStyleSheet(PRIMARY_BTN_STYLE)
        elif state == TimerState.RUNNING:
            self.btn_action.setText("Pause")
            self.btn_action.setStyleSheet(PAUSE_BTN_STYLE)
        elif state == TimerState.PAUSED:
            self.btn_action.setText("Resume")
            self.btn_action.setStyleSheet(PRIMARY_BTN_STYLE)
