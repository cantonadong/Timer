import ctypes
import os
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QApplication, QShortcut,
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QKeySequence

from core.timer_engine import TimerEngine, TimerMode, TimerState
from core.audio import AudioPlayer
from ui.styles import (
    BG_WINDOW, TEXT_TERTIARY, TEXT_SECONDARY,
    SEPARATOR, GREEN_ACTIVE, ACCENT, ACCENT_DARK,
)
from ui.display import TimeDisplay
from ui.mode_toggle import ModeToggle
from ui.controls import ControlPanel
from ui.presets import PresetBar, MAX_PRESETS

_MAX_CD_H = 99
_MAX_CD_M = 59
_MAX_CD_S = 59
_PRESET_BAR_H = 80   # fixed height so controls don't shift when bar is hidden
_HINT_ROW_H   = 18   # fixed height so controls don't shift when hint hides

def _resource(name: str) -> str:
    """Resolve a filename relative to the project root, works dev and PyInstaller --onefile."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), name)

_MP3_PATH = _resource("flow.mp3")


def _apply_win11_round_corners(hwnd):
    try:
        val = ctypes.c_int(2)  # DWMWCP_ROUND
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(val), ctypes.sizeof(val))
    except Exception:
        pass


# ── Traffic-light buttons ────────────────────────────────────────────────────

class _TrafficBtn(QPushButton):
    def __init__(self, color, symbol, parent=None):
        super().__init__(parent)
        self._color = color
        self._symbol = symbol
        self.setFixedSize(13, 13)
        self.setCursor(Qt.PointingHandCursor)
        self._idle()

    def _idle(self):
        self.setText("")
        self.setStyleSheet(
            f"QPushButton {{ background: {self._color}; border-radius: 6px; border: none; }}"
        )

    def enterEvent(self, e):
        self.setText(self._symbol)
        self.setStyleSheet(
            f"QPushButton {{ background: {self._color}; border-radius: 6px; border: none;"
            f" font-size: 9px; font-weight: 900; color: rgba(0,0,0,0.6); }}"
        )

    def leaveEvent(self, e):
        self._idle()


# ── "Always on top" pin button ─────────────────────────────────────────────────

class _PinBtn(QPushButton):
    """Compact toggle chip. Inactive → subtle gray | Active → solid green"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setToolTip("Always on top")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(22)
        self.toggled.connect(self._refresh)
        self._refresh(False)

    def sizeHint(self):
        return QSize(48, 22)

    def _refresh(self, active: bool):
        if active:
            self.setText("Top")
            self.setStyleSheet(
                f"QPushButton {{"
                f"  background: {GREEN_ACTIVE};"
                f"  color: white;"
                f"  border: none;"
                f"  border-radius: 6px;"
                f"  font-size: 11px;"
                f"  font-weight: 700;"
                f"  padding: 0 8px;"
                f"}}"
                f"QPushButton:hover {{ background: #2BB358; }}"
            )
        else:
            self.setText("Top")
            self.setStyleSheet(
                f"QPushButton {{"
                f"  background: rgba(142,142,147,0.13);"
                f"  color: {TEXT_TERTIARY};"
                f"  border: none;"
                f"  border-radius: 6px;"
                f"  font-size: 11px;"
                f"  font-weight: 500;"
                f"  padding: 0 8px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background: rgba(142,142,147,0.22);"
                f"  color: {TEXT_SECONDARY};"
                f"}}"
            )


# ── Draggable title bar ───────────────────────────────────────────────────────

class TitleBar(QWidget):
    def __init__(self, title="Timer", parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)

        self.btn_close    = _TrafficBtn("#FF5F57", "✕")
        self.btn_minimize = _TrafficBtn("#FFBD2E", "─")
        self.btn_close.clicked.connect(lambda: self.window().close())
        self.btn_minimize.clicked.connect(lambda: self.window().showMinimized())

        layout.addWidget(self.btn_close)
        layout.addWidget(self.btn_minimize)
        layout.addStretch()

        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"color: {TEXT_TERTIARY}; font-size: 13px; font-weight: 600;"
            " letter-spacing: 0.5px; background: transparent;"
        )
        layout.addWidget(lbl)
        layout.addStretch()

        self.pin_btn = _PinBtn()
        self.pin_btn.toggled.connect(self._toggle_pin)
        layout.addWidget(self.pin_btn)

    def _toggle_pin(self, pinned: bool):
        # Use Win32 SetWindowPos directly — avoids the Qt hide/show cycle that causes flicker.
        _HWND_TOPMOST   = ctypes.c_void_p(-1)
        _HWND_NOTOPMOST = ctypes.c_void_p(-2)
        _SWP_NOSIZE     = 0x0001
        _SWP_NOMOVE     = 0x0002
        _SWP_NOACTIVATE = 0x0010
        try:
            ctypes.windll.user32.SetWindowPos(
                int(self.window().winId()),
                _HWND_TOPMOST if pinned else _HWND_NOTOPMOST,
                0, 0, 0, 0,
                _SWP_NOSIZE | _SWP_NOMOVE | _SWP_NOACTIVATE,
            )
        except Exception:
            pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.window().move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = TimerEngine()
        self._finish_handled = False
        self._initial_show_done = False

        # Separate H/M/S — no carry-over between segments
        self._cd_h = 0
        self._cd_m = 5
        self._cd_s = 0

        self._audio = AudioPlayer(_MP3_PATH, plays=3)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedSize(420, 555)
        self.setStyleSheet(
            f"QWidget {{ background-color: {BG_WINDOW}; font-family: 'Segoe UI'; }}"
        )

        self._build_ui()
        self._wire_signals()
        self._setup_shortcuts()

        self._on_mode_changed(TimerMode.COUNTDOWN)

        self._poll = QTimer(self)
        self._poll.setInterval(50)
        self._poll.timeout.connect(self._on_tick)
        self._poll.start()

    def showEvent(self, event):
        super().showEvent(event)
        _apply_win11_round_corners(int(self.winId()))
        if not self._initial_show_done:
            self._initial_show_done = True
            screen = QApplication.primaryScreen().availableGeometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2,
            )

    # ── Build UI ──────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.title_bar = TitleBar("Timer")
        root.addWidget(self.title_bar)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {SEPARATOR};")
        root.addWidget(sep)

        content = QWidget()
        content.setStyleSheet(f"background: {BG_WINDOW};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 16, 20, 20)
        cl.setSpacing(0)

        # Mode toggle — centered
        toggle_row = QHBoxLayout()
        self.mode_toggle = ModeToggle()
        toggle_row.addStretch()
        toggle_row.addWidget(self.mode_toggle)
        toggle_row.addStretch()
        cl.addLayout(toggle_row)

        cl.addSpacing(10)

        # Time display
        self.time_display = TimeDisplay()
        cl.addWidget(self.time_display)

        cl.addSpacing(2)

        # ── Hint row (fixed height so layout is stable across modes) ──────
        hint_area = QWidget()
        hint_area.setFixedHeight(_HINT_ROW_H)
        hint_layout = QHBoxLayout(hint_area)
        hint_layout.setContentsMargins(0, 0, 0, 0)
        hint_layout.setSpacing(0)

        self.scroll_hint = QLabel("scroll to adjust")
        self.scroll_hint.setAlignment(Qt.AlignCenter)
        self.scroll_hint.setStyleSheet(
            f"color: {TEXT_TERTIARY}; font-size: 11px; background: transparent;"
        )
        self.scroll_hint.setVisible(False)

        self.add_preset_btn = QPushButton("+ add as preset")
        self.add_preset_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background: transparent;"
            f"  color: {ACCENT};"
            f"  border: none;"
            f"  font-size: 11px;"
            f"  font-weight: 500;"
            f"  padding: 0;"
            f"}}"
            f"QPushButton:hover {{ color: {ACCENT_DARK}; }}"
        )
        self.add_preset_btn.setVisible(False)
        self.add_preset_btn.clicked.connect(self._on_add_as_preset)

        hint_layout.addStretch(1)
        hint_layout.addWidget(self.scroll_hint)
        hint_layout.addSpacing(10)
        hint_layout.addWidget(self.add_preset_btn)
        hint_layout.addStretch(1)

        cl.addWidget(hint_area)
        cl.addSpacing(14)

        # ── Preset area (fixed height so controls don't shift when hidden) ─
        preset_area = QWidget()
        preset_area.setFixedHeight(_PRESET_BAR_H)
        preset_inner = QVBoxLayout(preset_area)
        preset_inner.setContentsMargins(0, 0, 0, 0)
        preset_inner.setSpacing(0)
        self.preset_bar = PresetBar()
        preset_inner.addWidget(self.preset_bar)
        cl.addWidget(preset_area)

        cl.addSpacing(14)

        # Controls
        self.controls = ControlPanel()
        cl.addWidget(self.controls)

        cl.addStretch()
        root.addWidget(content)

    # ── Signals ───────────────────────────────────────────────────────────

    def _wire_signals(self):
        self.mode_toggle.mode_changed.connect(self._on_mode_changed)
        self.preset_bar.preset_selected.connect(self._on_preset_selected)
        self.preset_bar.preset_deleted.connect(self._refresh_ui)
        self.time_display.scroll_segment.connect(self._on_scroll)
        self.controls.start_clicked.connect(self._on_start)
        self.controls.pause_clicked.connect(self._on_pause)
        self.controls.resume_clicked.connect(self._on_resume)
        self.controls.reset_clicked.connect(self._on_reset)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Space),  self, self._space_key)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self._on_reset)
        for i, key in enumerate([Qt.Key_1, Qt.Key_2, Qt.Key_3]):
            QShortcut(QKeySequence(key), self, lambda idx=i: self._trigger_preset(idx))

    # ── Helpers ───────────────────────────────────────────────────────────

    @property
    def _countdown_secs(self) -> int:
        return self._cd_h * 3600 + self._cd_m * 60 + self._cd_s

    def _sync_hms_from_secs(self, secs: int):
        self._cd_h = secs // 3600
        self._cd_m = (secs % 3600) // 60
        self._cd_s = secs % 60

    def _refresh_ui(self):
        """Full UI state refresh — call whenever mode, state, or time changes."""
        is_countdown = self.engine.mode == TimerMode.COUNTDOWN
        is_idle      = self.engine.state == TimerState.IDLE

        # Scroll on display: only countdown + idle
        self.time_display.set_scroll_enabled(is_countdown and is_idle)

        # Preset bar + hint row: only in countdown mode
        self.preset_bar.setVisible(is_countdown)
        self.scroll_hint.setVisible(is_countdown)

        # "add as preset": countdown + idle + time > 0 + presets not full + no duplicate
        already_saved = any(
            p["seconds"] == self._countdown_secs
            for p in self.preset_bar._presets
        )
        can_add = (
            is_countdown
            and is_idle
            and self._countdown_secs > 0
            and len(self.preset_bar._presets) < MAX_PRESETS
            and not already_saved
        )
        self.add_preset_btn.setVisible(can_add)

        # Start button: gray when countdown + idle + time == 0
        if is_countdown and is_idle:
            self.controls.set_start_enabled(self._countdown_secs > 0)
        else:
            self.controls.set_start_enabled(True)

    def _make_preset_label(self) -> str:
        h, m, s = self._cd_h, self._cd_m, self._cd_s
        if h == 0 and m == 0:
            return f"{s} sec"
        if h == 0 and s == 0:
            return f"{m} min"
        if h == 0:
            return f"{m}:{s:02d}"
        return f"{h}:{m:02d}:{s:02d}"

    # ── Handlers ──────────────────────────────────────────────────────────

    def _on_mode_changed(self, mode):
        self.engine.reset()
        self.engine.mode = mode
        self._finish_handled = False
        self.controls.update_state(TimerState.IDLE)
        if mode == TimerMode.COUNTDOWN:
            self.time_display.set_time_ms(self._countdown_secs * 1000)
        else:
            self.time_display.set_time_ms(0)
        self._refresh_ui()

    def _on_preset_selected(self, seconds: int):
        self._sync_hms_from_secs(seconds)
        if self.engine.mode != TimerMode.COUNTDOWN:
            self.engine.reset()
            self.engine.mode = TimerMode.COUNTDOWN
            self._finish_handled = False
            self.mode_toggle.set_mode(TimerMode.COUNTDOWN)
            self.controls.update_state(TimerState.IDLE)
        self.time_display.set_time_ms(self._countdown_secs * 1000)
        self._refresh_ui()

    def _on_scroll(self, seg: str, delta: int):
        if self.engine.state == TimerState.RUNNING or self.engine.mode != TimerMode.COUNTDOWN:
            return
        if seg == "h":
            self._cd_h = (self._cd_h + delta) % (_MAX_CD_H + 1)
        elif seg == "m":
            self._cd_m = (self._cd_m + delta) % (_MAX_CD_M + 1)
        else:
            self._cd_s = ((self._cd_s // 5 + delta) * 5) % 60     # 0,5,10…55, wrapping
        self.time_display.set_time_ms(self._countdown_secs * 1000)
        self._refresh_ui()

    def _on_add_as_preset(self):
        self.preset_bar.add_quick(self._make_preset_label(), self._countdown_secs)
        self._refresh_ui()

    def _on_start(self):
        if self.engine.mode == TimerMode.COUNTDOWN:
            if self._countdown_secs <= 0:
                return
            self.engine.target_ms = self._countdown_secs * 1000
        self._finish_handled = False
        self.engine.start()
        self.controls.update_state(TimerState.RUNNING)
        self._refresh_ui()

    def _on_pause(self):
        self.engine.pause()
        self.controls.update_state(TimerState.PAUSED)
        self._refresh_ui()

    def _on_resume(self):
        self.engine.resume()
        self.controls.update_state(TimerState.RUNNING)
        self._refresh_ui()

    def _on_reset(self):
        self.engine.reset()
        self._finish_handled = False
        self.time_display.stop_flash()
        self._audio.stop()
        self._cd_h = 0
        self._cd_m = 0
        self._cd_s = 0
        self.time_display.set_time_ms(0)
        self.controls.update_state(TimerState.IDLE)
        self._refresh_ui()

    def _space_key(self):
        st = self.engine.state
        if st == TimerState.IDLE:
            self._on_start()
        elif st == TimerState.RUNNING:
            self._on_pause()
        else:
            self._on_resume()

    def _trigger_preset(self, index: int):
        if index < len(self.preset_bar._presets):
            self._on_preset_selected(self.preset_bar._presets[index]["seconds"])

    # ── Poll ──────────────────────────────────────────────────────────────

    def _on_tick(self):
        if self.engine.state == TimerState.IDLE:
            return
        if self.engine.is_finished and not self._finish_handled:
            self._finish_handled = True
            self._on_countdown_finished()
            return
        if self.engine.mode == TimerMode.COUNTUP:
            self.time_display.set_time_ms(self.engine.current_elapsed_ms)
        else:
            self.time_display.set_time_ms(self.engine.remaining_ms)

    def _on_countdown_finished(self):
        self.engine.reset()
        self.time_display.set_time_ms(0)
        self.controls.update_state(TimerState.IDLE)
        self._refresh_ui()

        # Disable Start/Pause while alarm plays
        self.controls.btn_action.setEnabled(False)

        self.time_display.start_flash()

        if self._audio.available:
            try:
                self._audio.finished.disconnect()
            except TypeError:
                pass
            self._audio.finished.connect(self._on_alarm_done)
            self._audio.play()
        else:
            QApplication.beep()
            QTimer.singleShot(1680, self._on_alarm_done)

    def _on_alarm_done(self):
        """Called when the alarm finishes — stop flash, re-enable Start."""
        self.time_display.stop_flash()
        self._refresh_ui()   # re-enables Start if countdown time > 0
