"""
dbcCompare - DBC File Comparison Tool
A PyQt5 application for comparing CAN database (DBC) files.
"""

import datetime
import os
import sys
import traceback


def _excepthook(exc_type, exc_value, exc_tb):
    """Log unhandled exceptions to a file next to the executable."""
    if getattr(sys, "frozen", False):
        log_dir = os.path.dirname(sys.executable)
    else:
        log_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        log_path = os.path.join(log_dir, "dbcCompare_error.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 60 + "\n")
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("dbcCompare")
    app.setApplicationVersion("1.0.7")

    window = MainWindow()

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(args) >= 2 and os.path.exists(args[0]) and os.path.exists(args[1]):
        window.left_zone.set_file(args[0])
        window.right_zone.set_file(args[1])
        window._on_file_dropped("dbc1", args[0])
        window._on_file_dropped("dbc2", args[1])
        window._on_compare()

    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
