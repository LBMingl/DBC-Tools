"""Main window for dbcCompare application - redesigned to match original A1.0.7 layout."""

import csv
import os
import time

from PyQt5.QtCore import QPointF, QRectF, QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from parser.comparator import DBCComparator
from threads.compare_thread import CompareThread
from threads.parse_thread import ParseThread

STATUS_SAME = "Same"
STATUS_DIFF = "Different"
STATUS_ONLY_LEFT = "Only dbc1"
STATUS_ONLY_RIGHT = "Only dbc2"

STATUS_BG = {
    STATUS_SAME: QColor(255, 255, 255),
    STATUS_DIFF: QColor(255, 232, 204),
    STATUS_ONLY_LEFT: QColor(255, 221, 221),
    STATUS_ONLY_RIGHT: QColor(221, 221, 255),
}
STATUS_FG = {
    STATUS_SAME: QColor(0, 128, 0),
    STATUS_DIFF: QColor(200, 100, 0),
    STATUS_ONLY_LEFT: QColor(200, 0, 0),
    STATUS_ONLY_RIGHT: QColor(0, 80, 200),
}

CATEGORY_LABELS = [
    ("net", "NET", "net"),
    ("nodes", "Nodes", "nodes"),
    ("messages", "Messages", "messages"),
    ("signals", "Signals", "signals"),
    ("table_values", "Table values", "table"),
]

CATEGORY_NAMES = {key: label for key, label, _ in CATEGORY_LABELS}

CATEGORY_TOOLTIPS = {
    "net": "网络总览：节点 / 报文 / 信号 / 值表的差异统计",
    "nodes": "节点（ECU）对比：收发报文差异",
    "messages": "报文（Message）对比：ID、DLC、发送节点等",
    "signals": "信号（Signal）对比：起始位、长度、因子等",
    "table_values": "值表（枚举值）对比",
}
TT_COMPARE = "解析并对比两个已加载的 DBC 文件"
TT_VIEWMODE = "切换层级树视图（Network → Nodes/Messages → Signals）"


def make_icon(kind, size=44):
    """Draw a simple flat icon programmatically."""
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)

    dark = QColor(50, 50, 50)
    orange = QColor(255, 140, 0)
    blue = QColor(0, 120, 255)
    green = QColor(0, 150, 80)

    if kind == "net":
        p.setPen(QPen(dark, 2.2))
        p.setBrush(dark)
        p.drawLine(QPointF(22, 10), QPointF(10, 34))
        p.drawLine(QPointF(22, 10), QPointF(34, 34))
        p.drawLine(QPointF(10, 34), QPointF(34, 34))
        for pt in (QPointF(22, 10), QPointF(10, 34), QPointF(34, 34)):
            p.drawEllipse(pt, 5, 5)
    elif kind == "nodes":
        p.setPen(QPen(orange, 2.2))
        p.setBrush(orange)
        p.drawLine(QPointF(7, 22), QPointF(37, 22))
        for x in (11, 22, 33):
            p.drawEllipse(QPointF(x, 22), 4, 4)
    elif kind == "messages":
        p.setPen(QPen(dark, 2.2))
        p.setBrush(Qt.NoBrush)
        p.drawRect(5, 12, 34, 22)
        p.drawLine(QPointF(5, 12), QPointF(22, 26))
        p.drawLine(QPointF(39, 12), QPointF(22, 26))
    elif kind == "signals":
        p.setPen(QPen(blue, 2.4))
        path = QPainterPath()
        path.moveTo(5, 22)
        path.cubicTo(12, 8, 18, 8, 22, 22)
        path.cubicTo(26, 36, 32, 36, 39, 22)
        p.drawPath(path)
    elif kind == "table":
        p.setPen(QPen(dark, 2.2))
        p.drawRect(5, 8, 34, 28)
        p.drawLine(QPointF(5, 18), QPointF(39, 18))
        p.drawLine(QPointF(5, 28), QPointF(39, 28))
        p.drawLine(QPointF(17, 8), QPointF(17, 36))
        p.drawLine(QPointF(29, 8), QPointF(29, 36))
    elif kind == "compare":
        p.setPen(QPen(green, 3))
        p.drawLine(QPointF(7, 17), QPointF(37, 17))
        p.drawLine(QPointF(7, 17), QPointF(15, 11))
        p.drawLine(QPointF(7, 17), QPointF(15, 23))
        p.setPen(QPen(blue, 3))
        p.drawLine(QPointF(37, 27), QPointF(7, 27))
        p.drawLine(QPointF(37, 27), QPointF(29, 21))
        p.drawLine(QPointF(37, 27), QPointF(29, 33))
    elif kind == "view":
        p.setPen(QPen(dark, 2.2))
        p.setBrush(Qt.NoBrush)
        path = QPainterPath()
        path.moveTo(5, 22)
        path.cubicTo(13, 9, 31, 9, 39, 22)
        path.cubicTo(31, 35, 13, 35, 5, 22)
        p.drawPath(path)
        p.setBrush(dark)
        p.drawEllipse(QPointF(22, 22), 5, 5)
    elif kind == "grid":
        p.setPen(QPen(dark, 2))
        p.drawRect(7, 7, 30, 30)
        p.drawLine(QPointF(17, 7), QPointF(17, 37))
        p.drawLine(QPointF(27, 7), QPointF(27, 37))
        p.drawLine(QPointF(7, 17), QPointF(37, 17))
        p.drawLine(QPointF(7, 27), QPointF(37, 27))
    elif kind == "image":
        p.setPen(QPen(dark, 2))
        p.drawRect(6, 9, 32, 26)
        p.drawEllipse(QPointF(16, 18), 3, 3)
        p.drawLine(QPointF(6, 30), QPointF(16, 20))
        p.drawLine(QPointF(16, 20), QPointF(38, 35))
    elif kind == "search":
        p.setPen(QPen(dark, 2.6))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(18, 18), 9, 9)
        p.drawLine(QPointF(25, 25), QPointF(36, 36))
    elif kind == "home":
        p.setPen(QPen(dark, 2.4))
        p.setBrush(Qt.NoBrush)
        path = QPainterPath()
        path.moveTo(6, 20)
        path.lineTo(22, 8)
        path.lineTo(38, 20)
        p.drawPath(path)
        p.drawRect(11, 19, 22, 16)
        p.drawRect(19, 26, 7, 9)
    elif kind == "more":
        p.setPen(QPen(dark, 2))
        p.setBrush(dark)
        for x in (11, 22, 33):
            p.drawEllipse(QPointF(x, 22), 3, 3)
    elif kind == "mic":
        p.setPen(QPen(dark, 2.4))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(17, 5, 10, 17), 5, 5)
        p.drawArc(QRectF(12, 9, 20, 20), 180 * 16, -180 * 16)
        p.drawLine(QPointF(22, 30), QPointF(22, 35))
        p.drawLine(QPointF(15, 35), QPointF(29, 35))
    p.end()
    return QIcon(pm)


class DropZone(QFrame):
    """Drag-and-drop zone for loading a DBC file."""

    file_dropped = pyqtSignal(str)

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(62)
        self.setCursor(Qt.PointingHandCursor)
        self.title = title
        self.file_path = ""
        self.base_tooltip = f"拖放 .dbc 文件到此，或点击浏览（{title}）"
        self.setToolTip(self.base_tooltip)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)

        info = QLabel("i")
        info.setStyleSheet(
            "background: #999; color: white; border-radius: 9px;"
            "font-weight: bold;"
        )
        info.setFixedSize(18, 18)
        info.setAlignment(Qt.AlignCenter)
        info.setToolTip(f"Drop a .dbc file here, or click to browse ({title})")
        layout.addWidget(info)

        self.name_label = QLabel(f"Drag {title} here...")
        self.name_label.setStyleSheet("color: #999; font-size: 14px;")
        layout.addWidget(self.name_label, 1)

    def set_file(self, path):
        self.file_path = path
        self.name_label.setText(os.path.basename(path))
        self.name_label.setStyleSheet(
            "color: #000; font-size: 14px; font-weight: bold;"
        )
        self.setToolTip(path)

    def clear_file(self):
        self.file_path = ""
        self.name_label.setText(f"Drag {self.title} here...")
        self.name_label.setStyleSheet("color: #999; font-size: 14px;")
        self.setToolTip(self.base_tooltip)

    def _valid_path(self, mime):
        if not mime.hasUrls():
            return None
        for url in mime.urls():
            path = url.toLocalFile()
            if path.lower().endswith(".dbc"):
                return path
        return None

    def dragEnterEvent(self, event):
        if self._valid_path(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        path = self._valid_path(event.mimeData())
        if path:
            self.set_file(path)
            self.file_dropped.emit(path)
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            path, _ = QFileDialog.getOpenFileName(
                self, f"Select {self.title}", "", "DBC Files (*.dbc);;All Files (*)"
            )
            if path:
                self.set_file(path)
                self.file_dropped.emit(path)


class MainWindow(QMainWindow):
    """Main application window matching original dbcCompare A1.0.7 layout."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("dbcCompare A1.0.7")
        self.resize(1280, 860)

        self.left_data = None
        self.right_data = None
        self.comparator = DBCComparator()
        self.current_category = "net"
        self._hier = {"left": {}, "right": {}}

        self.compare_active = False
        self.compare_done = False
        self.start_time = 0.0
        self.parse_elapsed = 0.0
        self.compare_elapsed = 0.0

        self._init_ui()
        self._init_statusbar()

    # ------------------------------------------------------------------ UI
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(6)

        drop_layout = QHBoxLayout()
        drop_layout.setSpacing(6)
        self.left_zone = DropZone("dbc1")
        self.right_zone = DropZone("dbc2")
        self.left_zone.file_dropped.connect(lambda p: self._on_file_dropped("dbc1", p))
        self.right_zone.file_dropped.connect(lambda p: self._on_file_dropped("dbc2", p))
        drop_layout.addWidget(self.left_zone)
        drop_layout.addWidget(self.right_zone)
        root_layout.addLayout(drop_layout)

        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        content_splitter.setHandleWidth(6)
        content_splitter.addWidget(self._create_sidebar())

        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self._create_table_view())
        self.view_stack.addWidget(self._create_tree_view())
        content_splitter.addWidget(self.view_stack)
        content_splitter.setStretchFactor(1, 1)
        content_splitter.setSizes([110, 1100])

        self.detail_browser = QTextBrowser()
        self.detail_browser.setMinimumHeight(60)
        self.detail_browser.setHtml(
            "<p style='color:#888'>Load two DBC files and click Compare to see details.</p>"
        )

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(6)
        main_splitter.addWidget(content_splitter)
        main_splitter.addWidget(self.detail_browser)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setSizes([620, 180])

        root_layout.addWidget(main_splitter, 1)

    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar.setMinimumWidth(70)
        sidebar.setMaximumWidth(200)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(6)

        btn_style = """
            QToolButton { border: 1px solid transparent; border-radius: 6px; padding: 2px; }
            QToolButton:checked { background: #d0e4ff; border: 1px solid #7ab3ff; }
            QToolButton:hover { background: #eef4fb; }
            QToolButton:disabled { color: #aaa; }
        """

        self.category_buttons = {}
        self.category_group = QButtonGroup(self)
        self.category_group.setExclusive(True)

        for key, label, icon_kind in CATEGORY_LABELS:
            btn = QToolButton()
            btn.setText(label)
            btn.setIcon(make_icon(icon_kind))
            btn.setIconSize(QSize(40, 40))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setCheckable(True)
            btn.setMinimumSize(56, 62)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet(btn_style)
            btn.setToolTip(CATEGORY_TOOLTIPS[key])
            btn.clicked.connect(lambda checked, k=key: self._on_category_selected(k))
            self.category_group.addButton(btn)
            self.category_buttons[key] = btn
            layout.addWidget(btn)

        self.category_buttons["net"].setChecked(True)

        layout.addStretch()

        self.compare_btn = QToolButton()
        self.compare_btn.setText("Compare")
        self.compare_btn.setIcon(make_icon("compare"))
        self.compare_btn.setIconSize(QSize(40, 40))
        self.compare_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.compare_btn.setMinimumSize(56, 62)
        self.compare_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.compare_btn.setStyleSheet(btn_style)
        self.compare_btn.setEnabled(False)
        self.compare_btn.setToolTip(TT_COMPARE)
        self.compare_btn.clicked.connect(self._on_compare)
        layout.addWidget(self.compare_btn)

        self.viewmode_btn = QToolButton()
        self.viewmode_btn.setText("ViewMode")
        self.viewmode_btn.setIcon(make_icon("view"))
        self.viewmode_btn.setIconSize(QSize(40, 40))
        self.viewmode_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.viewmode_btn.setCheckable(True)
        self.viewmode_btn.setMinimumSize(56, 62)
        self.viewmode_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.viewmode_btn.setStyleSheet(btn_style)
        self.viewmode_btn.setEnabled(False)
        self.viewmode_btn.setToolTip(TT_VIEWMODE)
        self.viewmode_btn.clicked.connect(self._on_view_mode)
        layout.addWidget(self.viewmode_btn)

        return sidebar

    def _create_table_view(self):
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["dbc1", "dbc2", "Status"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemClicked.connect(self._on_table_clicked)
        return self.table

    def _create_tree_view(self):
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "dbc1", "dbc2", "Status"])
        self.tree.setColumnWidth(0, 260)
        self.tree.itemClicked.connect(self._on_tree_clicked)
        return self.tree

    def _init_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.elapsed_label = QLabel("Elapsed time: --/--")
        self.statusbar.addWidget(self.elapsed_label)

        self.statusbar.addPermanentWidget(self._create_status_toolbar())

        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.timeout.connect(self._update_elapsed)
        self.elapsed_timer.start(100)

    def _create_status_toolbar(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        export_btn = self._status_icon_btn("grid", "导出当前表格为 CSV")
        export_btn.clicked.connect(self._export_csv)
        layout.addWidget(export_btn)

        shot_btn = self._status_icon_btn("image", "保存窗口截图")
        shot_btn.clicked.connect(self._save_screenshot)
        layout.addWidget(shot_btn)

        find_btn = self._status_icon_btn("search", "聚焦搜索框")
        find_btn.clicked.connect(self._focus_search)
        layout.addWidget(find_btn)

        home_btn = self._status_icon_btn("home", "重置：清空已加载文件与对比结果")
        home_btn.clicked.connect(self._reset)
        layout.addWidget(home_btn)

        more_btn = self._status_icon_btn("more", "更多（关于 / 退出）")
        more_menu = QMenu(self)
        about_action = more_menu.addAction("About")
        about_action.triggered.connect(self._show_about)
        more_menu.addSeparator()
        exit_action = more_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        more_btn.setMenu(more_menu)
        more_btn.setPopupMode(QToolButton.InstantPopup)
        layout.addWidget(more_btn)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setFixedWidth(190)
        self.search_edit.setToolTip("输入关键字，实时过滤当前表格 / 树中的行")
        self.search_edit.addAction(make_icon("mic", 16), QLineEdit.LeadingPosition)
        self.search_edit.textChanged.connect(self._on_search)
        layout.addWidget(self.search_edit)

        return widget

    def _status_icon_btn(self, kind, tooltip):
        btn = QToolButton()
        btn.setIcon(make_icon(kind, 22))
        btn.setIconSize(QSize(20, 20))
        btn.setToolTip(tooltip)
        btn.setAutoRaise(True)
        return btn

    # --------------------------------------------------------------- events
    def _on_file_dropped(self, side, path):
        if self.left_zone.file_path and self.right_zone.file_path:
            self.compare_btn.setEnabled(True)
        self.statusbar.showMessage(
            f"Loaded {side}: {os.path.basename(path)}", 4000
        )

    def _on_category_selected(self, key):
        self.current_category = key
        if not (self.left_data and self.right_data and self.comparator.diff_results):
            return
        self._populate_table()
        if key == "net":
            self._show_net_detail()
        else:
            self._show_category_detail(key)

    def _on_view_mode(self):
        if self.viewmode_btn.isChecked():
            self.view_stack.setCurrentWidget(self.tree)
        else:
            self.view_stack.setCurrentWidget(self.table)

    def _focus_search(self):
        self.search_edit.setFocus()
        self.search_edit.selectAll()

    def _on_search(self, text):
        text = text.lower().strip()
        if self.view_stack.currentWidget() is self.table:
            for row in range(self.table.rowCount()):
                match = False
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and text in item.text().lower():
                        match = True
                        break
                self.table.setRowHidden(row, not match)
        else:
            self._filter_tree(self.tree.invisibleRootItem(), text)

    def _filter_tree(self, parent_item, text):
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            self._filter_tree(child, text)
            if not text:
                child.setHidden(False)
            else:
                self_match = any(
                    text in (child.text(c) or "").lower()
                    for c in range(child.columnCount())
                )
                child_visible = any(
                    not child.child(j).isHidden()
                    for j in range(child.childCount())
                )
                child.setHidden(not (self_match or child_visible))

    # -------------------------------------------------------------- compare
    def _on_compare(self):
        left = self.left_zone.file_path
        right = self.right_zone.file_path

        if not left or not right:
            QMessageBox.warning(self, "Warning", "Please load both DBC files.")
            return

        if not os.path.exists(left):
            QMessageBox.warning(self, "Warning", f"File not found: {left}")
            return

        if not os.path.exists(right):
            QMessageBox.warning(self, "Warning", f"File not found: {right}")
            return

        self.compare_active = True
        self.compare_done = False
        self.start_time = time.monotonic()
        self.elapsed_label.setText("Elapsed time: 0.00s / --")
        self.compare_btn.setEnabled(False)
        self.statusbar.showMessage("Parsing DBC files...")

        self.parse_thread = ParseThread(left, right)
        self.parse_thread.parsing_done.connect(self._on_parsing_done)
        self.parse_thread.error_occurred.connect(self._on_parse_error)
        self.parse_thread.start()

    def _on_parsing_done(self, left_data, right_data):
        self.parse_elapsed = time.monotonic() - self.start_time
        self.left_data = left_data
        self.right_data = right_data
        self.statusbar.showMessage("Comparing...")

        self.compare_thread = CompareThread(left_data, right_data)
        self.compare_thread.compare_done.connect(self._on_compare_done)
        self.compare_thread.start()

    def _on_compare_done(self, results):
        self.compare_elapsed = (
            time.monotonic() - self.start_time - self.parse_elapsed
        )
        self.compare_done = True
        self.compare_active = False

        self.comparator.diff_results = results
        self._build_hierarchy_maps()
        self._update_column_headers()
        self._populate_table()
        self._populate_tree()

        if self.current_category == "net":
            self._show_net_detail()
        else:
            self._show_category_detail(self.current_category)

        self.compare_btn.setEnabled(True)
        self.viewmode_btn.setEnabled(True)
        self.statusbar.showMessage("Comparison complete.", 4000)

    def _on_parse_error(self, error_msg):
        self.compare_active = False
        QMessageBox.critical(self, "Error", f"Error parsing files:\n{error_msg}")
        self.compare_btn.setEnabled(True)
        self.elapsed_label.setText("Elapsed time: --/--")

    def _update_elapsed(self):
        if not self.compare_active and not self.compare_done:
            return
        if self.compare_done:
            self.elapsed_label.setText(
                f"Elapsed time: {self.parse_elapsed:.2f}s / {self.compare_elapsed:.2f}s"
            )
        else:
            total = time.monotonic() - self.start_time
            self.elapsed_label.setText(f"Elapsed time: {total:.2f}s / --")

    def _update_column_headers(self):
        left_name = os.path.basename(self.left_zone.file_path)
        right_name = os.path.basename(self.right_zone.file_path)
        self.table.setHorizontalHeaderLabels([left_name, right_name, "Status"])
        self.tree.setHeaderLabels(["Name", left_name, right_name, "Status"])

    # ------------------------------------------------------------ populate
    def _populate_table(self):
        self.table.setRowCount(0)
        if not self.comparator.diff_results or not self.left_data:
            return
        if self.current_category == "net":
            self._populate_net_table()
        else:
            self._populate_category_table(self.current_category)

    def _populate_net_table(self):
        summary = self.comparator.get_summary()
        rows = [
            ("Nodes", "nodes"),
            ("Messages", "messages"),
            ("Signals", "signals"),
            ("Table values", "table_values"),
        ]
        self.table.setRowCount(len(rows))
        for i, (label, key) in enumerate(rows):
            s = summary[key]
            left_count, right_count = self._counts(key)
            parts = []
            if s["only_left"]:
                parts.append(f"{s['only_left']} only dbc1")
            if s["only_right"]:
                parts.append(f"{s['only_right']} only dbc2")
            if s["different"]:
                parts.append(f"{s['different']} different")
            status_text = ", ".join(parts) if parts else STATUS_SAME

            texts = [
                f"{label} ({left_count})",
                f"{label} ({right_count})",
                status_text,
            ]
            status = STATUS_DIFF if parts else STATUS_SAME
            for col, text in enumerate(texts):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 2:
                    item.setForeground(STATUS_FG[status])
                item.setBackground(STATUS_BG[status])
                self.table.setItem(i, col, item)

    def _populate_category_table(self, cat):
        self._ensure_hier()
        left_objs = set(self.left_data[cat].keys())
        right_objs = set(self.right_data[cat].keys())
        all_names = sorted(left_objs | right_objs)

        self.table.setRowCount(len(all_names))
        for i, name in enumerate(all_names):
            in_left = name in left_objs
            in_right = name in right_objs

            if in_left and in_right:
                status = (
                    STATUS_DIFF
                    if self._is_different(cat, name)
                    else STATUS_SAME
                )
            elif in_left:
                status = STATUS_ONLY_LEFT
            else:
                status = STATUS_ONLY_RIGHT

            texts = [
                self._cell_text(cat, name, "left") if in_left else "",
                self._cell_text(cat, name, "right") if in_right else "",
                status,
            ]
            for col, text in enumerate(texts):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if col == 2:
                    item.setForeground(STATUS_FG[status])
                item.setBackground(STATUS_BG[status])
                self.table.setItem(i, col, item)

    def _populate_tree(self):
        self.tree.clear()
        if not self.left_data or not self.right_data:
            return

        bold = QFont("Arial", 9, QFont.Bold)
        net = QTreeWidgetItem(["Network", "", "", ""])
        net.setFont(0, QFont("Arial", 10, QFont.Bold))
        self.tree.addTopLevelItem(net)

        # Nodes
        nodes_item = QTreeWidgetItem(["Nodes", "", "", ""])
        nodes_item.setFont(0, bold)
        net.addChild(nodes_item)

        left_nodes = set(self.left_data["nodes"].keys())
        right_nodes = set(self.right_data["nodes"].keys())
        for name in sorted(left_nodes | right_nodes):
            item = self._make_tree_item(
                name,
                name in left_nodes,
                name in right_nodes,
                self._node_status(name, left_nodes, right_nodes),
            )
            nodes_item.addChild(item)

        # Messages (with signals as children)
        messages_item = QTreeWidgetItem(["Messages", "", "", ""])
        messages_item.setFont(0, bold)
        net.addChild(messages_item)

        left_msgs = set(self.left_data["messages"].keys())
        right_msgs = set(self.right_data["messages"].keys())
        for name in sorted(left_msgs | right_msgs):
            status = self._message_status(name, left_msgs, right_msgs)
            msg_item = self._make_tree_item(
                name, name in left_msgs, name in right_msgs, status
            )
            messages_item.addChild(msg_item)

            left_sigs = {}
            right_sigs = {}
            if name in left_msgs:
                for sig in self.left_data["messages"][name].signals:
                    left_sigs[sig.name] = sig
            if name in right_msgs:
                for sig in self.right_data["messages"][name].signals:
                    right_sigs[sig.name] = sig

            for sig_name in sorted(set(left_sigs) | set(right_sigs)):
                sig_status = self._signal_status(sig_name, left_sigs, right_sigs)
                sig_item = self._make_tree_item(
                    sig_name,
                    sig_name in left_sigs,
                    sig_name in right_sigs,
                    sig_status,
                )
                msg_item.addChild(sig_item)

        # Table values
        tables_item = QTreeWidgetItem(["Table values", "", "", ""])
        tables_item.setFont(0, bold)
        net.addChild(tables_item)

        left_tables = set(self.left_data["table_values"].keys())
        right_tables = set(self.right_data["table_values"].keys())
        for name in sorted(left_tables | right_tables):
            status = ""
            if name in left_tables and name in right_tables:
                lv = self.left_data["table_values"][name].values
                rv = self.right_data["table_values"][name].values
                status = STATUS_DIFF if lv != rv else ""
            elif name in left_tables:
                status = STATUS_ONLY_LEFT
            else:
                status = STATUS_ONLY_RIGHT
            item = self._make_tree_item(
                name, name in left_tables, name in right_tables, status
            )
            tables_item.addChild(item)

        self.tree.expandAll()

    def _make_tree_item(self, name, in_left, in_right, status):
        item = QTreeWidgetItem([
            name,
            "Y" if in_left else "",
            "Y" if in_right else "",
            status,
        ])
        fg = STATUS_FG.get(status)
        if fg:
            item.setForeground(3, fg)
        return item

    def _node_status(self, name, left_nodes, right_nodes):
        if name in left_nodes and name in right_nodes:
            ln = self.left_data["nodes"][name]
            rn = self.right_data["nodes"][name]
            if ln.tx_messages != rn.tx_messages or ln.rx_messages != rn.rx_messages:
                return STATUS_DIFF
            return ""
        if name in left_nodes:
            return STATUS_ONLY_LEFT
        return STATUS_ONLY_RIGHT

    def _message_status(self, name, left_msgs, right_msgs):
        if name in left_msgs and name in right_msgs:
            lm = self.left_data["messages"][name]
            rm = self.right_data["messages"][name]
            if lm.id != rm.id or lm.dlc != rm.dlc or lm.transmitter != rm.transmitter:
                return STATUS_DIFF
            left_sigs = set(s.name for s in lm.signals)
            right_sigs = set(s.name for s in rm.signals)
            if left_sigs != right_sigs:
                return STATUS_DIFF
            return ""
        if name in left_msgs:
            return STATUS_ONLY_LEFT
        return STATUS_ONLY_RIGHT

    def _signal_status(self, name, left_sigs, right_sigs):
        if name in left_sigs and name in right_sigs:
            ls = left_sigs[name]
            rs = right_sigs[name]
            if (ls.start_bit != rs.start_bit or ls.length != rs.length
                    or ls.factor != rs.factor or ls.offset != rs.offset):
                return STATUS_DIFF
            return ""
        if name in left_sigs:
            return STATUS_ONLY_LEFT
        return STATUS_ONLY_RIGHT

    # ------------------------------------------------------------ details
    def _show_net_detail(self):
        if not self.comparator.diff_results or not self.left_data:
            return
        summary = self.comparator.get_summary()
        html = (
            "<h2>Network Overview</h2>"
            "<table border='1' cellpadding='4' cellspacing='0'>"
            "<tr><th>Category</th><th>dbc1</th><th>dbc2</th><th>Status</th></tr>"
        )
        for label, key in [
            ("Nodes", "nodes"),
            ("Messages", "messages"),
            ("Signals", "signals"),
            ("Table values", "table_values"),
        ]:
            s = summary[key]
            left_count, right_count = self._counts(key)
            parts = []
            if s["only_left"]:
                parts.append(f"{s['only_left']} only dbc1")
            if s["only_right"]:
                parts.append(f"{s['only_right']} only dbc2")
            if s["different"]:
                parts.append(f"{s['different']} different")
            status = ", ".join(parts) if parts else STATUS_SAME
            html += (
                f"<tr><td>{label}</td><td>{left_count}</td>"
                f"<td>{right_count}</td><td>{status}</td></tr>"
            )
        html += "</table>"
        self.detail_browser.setHtml(html)

    def _show_category_detail(self, cat):
        s = self.comparator.get_summary()[cat]
        left_count, right_count = self._counts(cat)
        label = CATEGORY_NAMES[cat]
        html = f"<h2>{label}</h2>"
        html += f"<p>dbc1: {left_count} items &nbsp;|&nbsp; dbc2: {right_count} items</p>"
        parts = []
        if s["only_left"]:
            parts.append(f"{s['only_left']} only in dbc1")
        if s["only_right"]:
            parts.append(f"{s['only_right']} only in dbc2")
        if s["different"]:
            parts.append(f"{s['different']} different")
        html += f"<p>{', '.join(parts) if parts else 'All items identical'}</p>"
        self.detail_browser.setHtml(html)

    def _show_item_detail(self, cat, name):
        label = CATEGORY_NAMES[cat]
        self._ensure_hier()
        html = f"<h2>{label}: {name}</h2>"
        for side_key, side_label, data in (
            ("left", "dbc1", self.left_data),
            ("right", "dbc2", self.right_data),
        ):
            obj = data[cat].get(name) if data else None
            if obj is None:
                html += f"<h3>{side_label}: <span style='color:#c00'>not present</span></h3>"
                continue
            path = self._hier_line(cat, name, side_key)
            html += f"<h3>{side_label}</h3>"
            if path:
                html += f"<p><b>Hierarchy:</b> {path}</p>"
            html += "<ul>"
            if cat == "nodes":
                html += f"<li>TX messages: {sorted(obj.tx_messages)}</li>"
                html += f"<li>RX messages: {sorted(obj.rx_messages)}</li>"
                if obj.attributes:
                    html += f"<li>Attributes: {obj.attributes}</li>"
            elif cat == "messages":
                html += f"<li>ID: 0x{obj.id:X} ({obj.id})</li>"
                html += f"<li>DLC: {obj.dlc}</li>"
                html += f"<li>Transmitter (node): {obj.transmitter or '-'}</li>"
                html += f"<li>Signals: {[s.name for s in obj.signals]}</li>"
                if obj.comment:
                    html += f"<li>Comment: {obj.comment}</li>"
            elif cat == "signals":
                html += f"<li>Start bit: {obj.start_bit}</li>"
                html += f"<li>Length: {obj.length}</li>"
                html += f"<li>Byte order: {obj.byte_order}</li>"
                html += f"<li>Value type: {obj.value_type}</li>"
                html += f"<li>Factor: {obj.factor}</li>"
                html += f"<li>Offset: {obj.offset}</li>"
                html += f"<li>Range: [{obj.min_value}, {obj.max_value}]</li>"
                html += f"<li>Unit: {obj.unit}</li>"
                html += f"<li>Receivers: {sorted(obj.receivers)}</li>"
            elif cat == "table_values":
                for val in sorted(obj.values):
                    html += f"<li>{val}: {obj.values[val]}</li>"
            html += "</ul>"
        self.detail_browser.setHtml(html)

    def _on_table_clicked(self, item):
        cat = self.current_category
        if cat == "net":
            return
        row = item.row()
        text = self.table.item(row, 0).text() or self.table.item(row, 1).text()
        if not text:
            return
        name = text.split(" ")[0]
        self._show_item_detail(cat, name)

    def _on_tree_clicked(self, item, column):
        name = item.text(0)
        parent = item.parent()
        if parent is None:
            if name == "Network":
                self._show_net_detail()
            return
        grandparent = parent.parent() if parent else None
        if grandparent is None:
            return
        if parent.text(0) == "Nodes":
            self._show_item_detail("nodes", name)
        elif parent.text(0) == "Table values":
            self._show_item_detail("table_values", name)
        elif parent.text(0) == "Messages":
            self._show_item_detail("messages", name)
        else:
            self._show_item_detail("signals", name)

    # -------------------------------------------------------------- helpers
    def _counts(self, key):
        return len(self.left_data[key]), len(self.right_data[key])

    def _is_different(self, cat, name):
        return any(
            d["name"] == name
            for d in self.comparator.diff_results[cat]["different"]
        )

    def _build_hierarchy_maps(self):
        """Build per-side lookups: msg->node, sig->msgs, msg id->name."""
        self._hier = {}
        for side, data in (("left", self.left_data), ("right", self.right_data)):
            msg_node = {}
            sig_msgs = {}
            id_msg = {}
            if data:
                for msg_name, msg in data["messages"].items():
                    msg_node[msg_name] = msg.transmitter
                    id_msg[msg.id] = msg_name
                    for sig in msg.signals:
                        names = sig_msgs.setdefault(sig.name, [])
                        if msg_name not in names:
                            names.append(msg_name)
            self._hier[side] = {
                "msg_node": msg_node,
                "sig_msgs": sig_msgs,
                "id_msg": id_msg,
            }

    def _ensure_hier(self):
        if "sig_msgs" not in self._hier.get("left", {}):
            self._build_hierarchy_maps()

    def _hier_line(self, cat, name, side):
        """Full ownership path for an item, e.g. Node -> Message -> Signal."""
        hier = self._hier.get(side, {})
        if cat == "messages":
            node = hier.get("msg_node", {}).get(name, "")
            return f"Node {node or '?'} → Message {name}"
        if cat == "signals":
            parents = hier.get("sig_msgs", {}).get(name, [])
            if not parents:
                return f"Signal {name} (no parent message found)"
            parts = []
            for msg_name in parents:
                node = hier.get("msg_node", {}).get(msg_name, "?")
                parts.append(f"Node {node} → Message {msg_name} → Signal {name}")
            return "<br>".join(parts)
        if cat == "table_values":
            msg_id_str, sig_name = name.split("_", 1)
            try:
                msg_id = int(msg_id_str)
            except ValueError:
                return f"Signal {sig_name} (unresolved message id {msg_id_str})"
            msg_name = hier.get("id_msg", {}).get(msg_id)
            node = hier.get("msg_node", {}).get(msg_name, "?") if msg_name else "?"
            msg_txt = msg_name or f"ID {msg_id}"
            return f"Node {node} → Message {msg_txt} → Signal {sig_name}"
        return ""

    def _cell_text(self, cat, name, side):
        data = self.left_data if side == "left" else self.right_data
        hier = self._hier[side]
        if cat == "nodes":
            node = data["nodes"][name]
            return f"{name} (TX:{len(node.tx_messages)}, RX:{len(node.rx_messages)})"
        if cat == "messages":
            msg = data["messages"][name]
            tx = msg.transmitter or "-"
            return f"{name} (0x{msg.id:X}, DLC {msg.dlc}, TX: {tx})"
        if cat == "signals":
            sig = data["signals"][name]
            parents = hier["sig_msgs"].get(name, [])
            prefix = " / ".join(parents) + ", " if parents else ""
            return f"{name} ({prefix}{sig.start_bit}|{sig.length}, {sig.factor}/{sig.offset})"
        if cat == "table_values":
            table = data["table_values"][name]
            msg_id_str, sig_name = name.split("_", 1)
            try:
                msg_name = hier["id_msg"].get(int(msg_id_str))
            except ValueError:
                msg_name = None
            owner = msg_name or f"ID {msg_id_str}"
            return f"{name} ({owner}/{sig_name}, {len(table.values)} values)"
        return name

    # ------------------------------------------------------------- toolbar
    def _export_csv(self):
        if self.view_stack.currentWidget() is not self.table:
            self.view_stack.setCurrentWidget(self.table)
        if self.table.rowCount() == 0:
            self.statusbar.showMessage("Nothing to export.", 3000)
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "comparison.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            headers = [
                self.table.horizontalHeaderItem(c).text()
                for c in range(self.table.columnCount())
            ]
            writer.writerow(headers)
            for row in range(self.table.rowCount()):
                if self.table.isRowHidden(row):
                    continue
                writer.writerow([
                    self.table.item(row, c).text() if self.table.item(row, c) else ""
                    for c in range(self.table.columnCount())
                ])
        self.statusbar.showMessage(f"Exported: {path}", 4000)

    def _save_screenshot(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot", "screenshot.png", "PNG Images (*.png)"
        )
        if not path:
            return
        self.grab().save(path)
        self.statusbar.showMessage(f"Saved: {path}", 4000)

    def _reset(self):
        self.left_zone.clear_file()
        self.right_zone.clear_file()
        self.left_data = None
        self.right_data = None
        self.comparator = DBCComparator()
        self._hier = {"left": {}, "right": {}}
        self.compare_active = False
        self.compare_done = False

        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(["dbc1", "dbc2", "Status"])
        self.tree.clear()
        self.tree.setHeaderLabels(["Name", "dbc1", "dbc2", "Status"])
        self.detail_browser.setHtml(
            "<p style='color:#888'>Load two DBC files and click Compare to see details.</p>"
        )
        self.search_edit.clear()
        self.elapsed_label.setText("Elapsed time: --/--")
        self.current_category = "net"
        self.category_buttons["net"].setChecked(True)
        self.view_stack.setCurrentWidget(self.table)
        self.compare_btn.setEnabled(False)
        self.viewmode_btn.setEnabled(False)
        self.viewmode_btn.setChecked(False)
        self.statusbar.showMessage("Reset", 3000)

    def _show_about(self):
        QMessageBox.about(
            self,
            "About dbcCompare",
            "<h3>dbcCompare A1.0.7</h3>"
            "<p>Compare two CAN database (DBC) files.</p>"
            "<p>PyQt5 reimplementation based on the original dbcCompare "
            "by Sava Claudiu Gigel.</p>",
        )
