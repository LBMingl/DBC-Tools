"""Compare view widget for displaying comparison results."""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QPushButton,
    QLineEdit,
    QSplitter,
    QTextBrowser,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class CompareView(QWidget):
    """Widget for displaying comparison results."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        self.title_label = QLabel("Comparison Results")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(self.title_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self._on_search)
        header_layout.addWidget(self.search_edit)

        layout.addLayout(header_layout)

        splitter = QSplitter(Qt.Vertical)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Details"])
        self.tree_widget.setColumnCount(2)
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        splitter.addWidget(self.tree_widget)

        self.detail_browser = QTextBrowser()
        self.detail_browser.setOpenExternalLinks(False)
        splitter.addWidget(self.detail_browser)

        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

    def show_only_left(self, items, category):
        """Show items only in left file."""
        self.tree_widget.clear()
        self.title_label.setText(f"Only in Left File - {category}")

        for item_name in items:
            tree_item = QTreeWidgetItem([item_name, "Only in left file"])
            tree_item.setForeground(0, QColor(Qt.red))
            self.tree_widget.addTopLevelItem(tree_item)

        self.tree_widget.expandAll()

    def show_only_right(self, items, category):
        """Show items only in right file."""
        self.tree_widget.clear()
        self.title_label.setText(f"Only in Right File - {category}")

        for item_name in items:
            tree_item = QTreeWidgetItem([item_name, "Only in right file"])
            tree_item.setForeground(0, QColor(Qt.blue))
            self.tree_widget.addTopLevelItem(tree_item)

        self.tree_widget.expandAll()

    def show_different(self, items, category):
        """Show different items."""
        self.tree_widget.clear()
        self.title_label.setText(f"Different - {category}")

        for item_data in items:
            item_name = item_data["name"]
            diffs = item_data["diffs"]

            tree_item = QTreeWidgetItem([item_name, "; ".join(diffs)])
            tree_item.setForeground(0, QColor(Qt.darkYellow))
            self.tree_widget.addTopLevelItem(tree_item)

        self.tree_widget.expandAll()

    def _on_item_clicked(self, item, column):
        """Handle item click."""
        name = item.text(0)
        details = item.text(1)
        self.detail_browser.setHtml(
            f"<h3>{name}</h3><p>{details}</p>"
        )

    def _on_search(self, text):
        """Handle search text change."""
        if not text:
            for i in range(self.tree_widget.topLevelItemCount()):
                self.tree_widget.topLevelItem(i).setHidden(False)
            return

        text_lower = text.lower()
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            name = item.text(0).lower()
            details = item.text(1).lower()
            item.setHidden(text_lower not in name and text_lower not in details)
