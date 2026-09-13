"""Thread for parsing DBC files."""

from PyQt5.QtCore import QThread, pyqtSignal
from parser.dbc_parser import DBCParser


class ParseThread(QThread):
    """Thread for parsing DBC files in background."""

    parsing_done = pyqtSignal(dict, dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, left_file, right_file, parent=None):
        super().__init__(parent)
        self.left_file = left_file
        self.right_file = right_file

    def run(self):
        """Run the parsing thread."""
        try:
            left_parser = DBCParser()
            left_data = left_parser.parse_file(self.left_file)

            right_parser = DBCParser()
            right_data = right_parser.parse_file(self.right_file)

            self.parsing_done.emit(left_data, right_data)
        except Exception as e:
            self.error_occurred.emit(str(e))
