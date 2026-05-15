from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

# --- Color palette (macOS system colors) ---
BG_WINDOW   = "#F2F2F7"
BG_CARD     = "#FFFFFF"
BG_TOGGLE   = "#E5E5EA"
ACCENT      = "#007AFF"
ACCENT_DARK = "#0062CC"
PAUSE_COLOR = "#FF9500"          # macOS system orange — used for Pause state
PAUSE_DARK  = "#CC7700"
DANGER      = "#FF3B30"
DANGER_DARK = "#CC2F26"
GREEN_ACTIVE  = "#34C759"        # macOS green — used for "always on top" active
TEXT_PRIMARY   = "#1C1C1E"
TEXT_SECONDARY = "#3A3A3C"
TEXT_TERTIARY  = "#8E8E93"
SEPARATOR      = "#E5E5EA"

# Consistent rounded-rectangle radius (not pill/capsule)
BTN_RADIUS = 10


def make_shadow(widget, blur=16, offset_y=3, opacity=20):
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(0, offset_y)
    effect.setColor(QColor(0, 0, 0, opacity))
    widget.setGraphicsEffect(effect)
    return effect


# --- Stylesheet fragments ---

CARD_STYLE = f"""
    background-color: {BG_CARD};
    border-radius: 16px;
"""

PRIMARY_BTN_STYLE = f"""
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: {BTN_RADIUS}px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}
QPushButton:hover {{
    background-color: {ACCENT_DARK};
}}
QPushButton:pressed {{
    background-color: {ACCENT_DARK};
}}
QPushButton:disabled {{
    background-color: {BG_TOGGLE};
    color: {TEXT_TERTIARY};
}}
"""

PAUSE_BTN_STYLE = f"""
QPushButton {{
    background-color: {PAUSE_COLOR};
    color: white;
    border: none;
    border-radius: {BTN_RADIUS}px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}
QPushButton:hover {{
    background-color: {PAUSE_DARK};
}}
QPushButton:pressed {{
    background-color: {PAUSE_DARK};
}}
"""

DANGER_BTN_STYLE = f"""
QPushButton {{
    background-color: {BG_CARD};
    color: {DANGER};
    border: 1.5px solid {SEPARATOR};
    border-radius: {BTN_RADIUS}px;
    font-size: 14px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {BG_WINDOW};
    border-color: {DANGER};
}}
QPushButton:pressed {{
    background-color: {SEPARATOR};
}}
QPushButton:disabled {{
    color: {TEXT_TERTIARY};
    border-color: {SEPARATOR};
    background-color: {BG_CARD};
}}
"""

PRESET_BTN_STYLE = f"""
QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1.5px solid {SEPARATOR};
    border-radius: {BTN_RADIUS}px;
    font-size: 13px;
    font-weight: 500;
    padding: 5px 4px;
}}
QPushButton:hover {{
    background-color: #EBF3FF;
    border-color: {ACCENT};
    color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {SEPARATOR};
}}
"""

ADD_BTN_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: {ACCENT};
    border: none;
    font-size: 12px;
    font-weight: 500;
    padding: 0px;
}}
QPushButton:hover {{
    color: {ACCENT_DARK};
}}
"""

CONTEXT_MENU_STYLE = f"""
QMenu {{
    background-color: {BG_CARD};
    border: 1px solid {SEPARATOR};
    border-radius: 10px;
    padding: 4px 0px;
}}
QMenu::item {{
    padding: 7px 20px;
    font-size: 13px;
    border-radius: 6px;
    margin: 2px 4px;
}}
QMenu::item:selected {{
    background-color: {BG_WINDOW};
    color: {TEXT_PRIMARY};
}}
QMenu::separator {{
    height: 1px;
    background: {SEPARATOR};
    margin: 4px 12px;
}}
"""

DIALOG_STYLE = f"""
QDialog {{
    background-color: {BG_WINDOW};
}}
QLabel {{
    color: {TEXT_SECONDARY};
    font-size: 13px;
    background: transparent;
}}
QLineEdit, QTimeEdit {{
    background-color: {BG_CARD};
    border: 1.5px solid {SEPARATOR};
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 14px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QTimeEdit:focus {{
    border-color: {ACCENT};
}}
QTimeEdit::up-button, QTimeEdit::down-button {{
    border: none;
    background: transparent;
}}
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    padding: 7px 18px;
    min-width: 70px;
}}
QPushButton:hover {{
    background-color: {ACCENT_DARK};
}}
QPushButton[text="Cancel"] {{
    background-color: {BG_TOGGLE};
    color: {TEXT_PRIMARY};
}}
QPushButton[text="Cancel"]:hover {{
    background-color: {SEPARATOR};
}}
"""
