import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush


def _make_icon() -> QIcon:
    """Draw a simple clock icon at multiple sizes."""
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)

        # Blue filled circle
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#007AFF"))
        p.drawEllipse(0, 0, size, size)

        # White inner face
        m = max(1, size // 8)
        p.setBrush(QColor("white"))
        p.drawEllipse(m, m, size - 2 * m, size - 2 * m)

        # Clock hands — 10:10 style
        cx, cy = size / 2, size / 2
        r = size / 2 - m - 1
        import math
        pen = QPen(QColor("#007AFF"), max(1.0, size * 0.09), Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)

        # Hour hand (pointing ~10 o'clock)
        angle_h = math.radians(-60)   # 10 o'clock
        hr = r * 0.55
        p.drawLine(
            int(cx), int(cy),
            int(cx + hr * math.sin(angle_h)),
            int(cy - hr * math.cos(angle_h)),
        )
        # Minute hand (pointing ~2 o'clock)
        angle_m = math.radians(60)    # 2 o'clock
        mr = r * 0.75
        p.drawLine(
            int(cx), int(cy),
            int(cx + mr * math.sin(angle_m)),
            int(cy - mr * math.cos(angle_m)),
        )
        # Center dot
        p.setBrush(QColor("#007AFF"))
        p.setPen(Qt.NoPen)
        dot = max(1, size // 10)
        p.drawEllipse(int(cx - dot / 2), int(cy - dot / 2), dot, dot)

        p.end()
        icon.addPixmap(pix)
    return icon


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Timer")

    icon = _make_icon()
    app.setWindowIcon(icon)

    from ui.main_window import MainWindow
    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
