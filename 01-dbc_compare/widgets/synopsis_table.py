"""Synopsis table widget for displaying detailed information."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTextEdit,
    QLabel,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SynopsisTable(QWidget):
    """Widget for displaying detailed synopsis information."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Synopsis Table")
        self.resize(800, 600)
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        header_label = QLabel(":: Synopsis Table ::")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        splitter = QSplitter(Qt.Horizontal)

        self.left_text = QTextEdit()
        self.left_text.setReadOnly(True)
        self.left_text.setFont(QFont("Courier New", 10))
        splitter.addWidget(self.left_text)

        self.right_text = QTextEdit()
        self.right_text.setReadOnly(True)
        self.right_text.setFont(QFont("Courier New", 10))
        splitter.addWidget(self.right_text)

        splitter.setSizes([400, 400])
        layout.addWidget(splitter)

        self._show_default_text()

    def _show_default_text(self):
        """Show default text."""
        default_html = """
        <div style="color: #C2C2C2;">
        <p>No information available.</p>
        <p><b>HINT:</b> Select a valid CAN signal or CAN message.</p>
        </div>
        """
        self.left_text.setHtml(default_html)
        self.right_text.setHtml(default_html)

    def set_left_text(self, html_content):
        """Set left text content."""
        self.left_text.setHtml(html_content)

    def set_right_text(self, html_content):
        """Set right text content."""
        self.right_text.setHtml(html_content)

    def clear_data(self):
        """Clear all data."""
        self.left_text.clear()
        self.right_text.clear()
        self._show_default_text()

    def set_message_info(self, message_name, signal_structure, tx_nodes, rx_nodes):
        """Set message information."""
        html = f"""
        <h3>Message name:</h3>
        <p style="color: #2B65EC;">{message_name}</p>
        <br>
        <h3>Signal structure:</h3>
        <p>{signal_structure}</p>
        <br>
        <h3>Send by nodes:</h3>
        <p>{tx_nodes}</p>
        <br>
        <h3>Receive by nodes:</h3>
        <p>{rx_nodes}</p>
        """
        self.left_text.setHtml(html)

    def set_signal_info(self, signal_name, message_name, details):
        """Set signal information."""
        html = f"""
        <h3>Signal name:</h3>
        <p style="color: #2B65EC;">{signal_name}</p>
        <br>
        <h3>Belongs to message:</h3>
        <p>{message_name}</p>
        <br>
        <h3>Details:</h3>
        <p>{details}</p>
        """
        self.right_text.setHtml(html)
