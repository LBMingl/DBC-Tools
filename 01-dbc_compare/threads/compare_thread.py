"""Thread for comparing DBC files."""

from PyQt5.QtCore import QThread, pyqtSignal
from parser.comparator import DBCComparator


class CompareThread(QThread):
    """Thread for comparing DBC files in background."""

    compare_done = pyqtSignal(dict)

    def __init__(self, left_data, right_data, parent=None):
        super().__init__(parent)
        self.left_data = left_data
        self.right_data = right_data

    def run(self):
        """Run the comparison thread."""
        comparator = DBCComparator()
        comparator.load_dbc(self.left_data, self.right_data)
        results = comparator.compare()
        self.compare_done.emit(results)
