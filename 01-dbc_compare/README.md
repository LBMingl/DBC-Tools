# dbcCompare - DBC File Comparison Tool

A PyQt5 application for comparing CAN database (DBC) files.

## Features

- **DBC File Parsing**: Parse DBC files containing nodes, messages, signals, attributes, and table values
- **File Comparison**: Compare two DBC files and identify differences
- **Original A1.0.7 Layout**:
  - Left icon sidebar: NET / Nodes / Messages / Signals / Table values / Compare / ViewMode
  - Drag-and-drop zones for loading the two DBC files
  - Comparison table with `dbc1` / `dbc2` / `Status` columns, color-coded per row
  - ViewMode toggles the hierarchical tree (Network → Nodes/Messages → Signals)
  - Detail panel showing full information of the selected item
- **Search**: Filter rows in the table or tree from the status bar search box
- **Export**: Export the current table to CSV, save window screenshot
- **Elapsed time** display for parse and compare phases

## Requirements

- Python 3.11 or higher
- PyQt5 5.15 or higher

## Installation

1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running from Source

```bash
python main.py
```

## Building Executable

### Windows

Run the build script:
```bash
build.bat
```

Or manually:
```bash
pip install pyinstaller
pyinstaller dbcCompare.spec --clean
```

The executable will be in `dist/dbcCompare/dbcCompare.exe`

## Usage

1. **Load DBC Files**:
   - Drag and drop `.dbc` files onto the two drop zones at the top, or
   - Click a drop zone to browse for a file

2. **Compare**:
   - Click the "Compare" button in the left sidebar

3. **Browse Results**:
   - Switch category with the sidebar buttons (NET, Nodes, Messages, Signals, Table values)
   - Click a table row to see full details in the bottom panel
   - Click "ViewMode" to toggle the hierarchical tree view

4. **Search**:
   - Type in the search box (bottom right) to filter rows

## DBC File Format

This tool supports standard DBC (CAN database) files with:
- Node definitions (BU_)
- Message definitions (BO_)
- Signal definitions (SG_)
- Attribute definitions (BA_DEF_, BA_DEF_DEF_)
- Attribute values (BA_)
- Value tables (VAL_)
- Comments (CM_)

## Project Structure

```
New/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── dbcCompare.spec        # PyInstaller spec file
├── build.bat              # Build script (Windows)
├── parser/                # DBC parsing module
│   ├── __init__.py
│   ├── dbc_parser.py      # DBC file parser
│   ├── dbc_objects.py     # Data structures
│   └── comparator.py      # Comparison engine
├── gui/                   # GUI module
│   ├── __init__.py
│   └── main_window.py     # Main window
├── widgets/               # Custom widgets
│   ├── __init__.py
│   ├── compare_view.py    # Comparison view
│   └── synopsis_table.py  # Synopsis table
└── threads/               # Background threads
    ├── __init__.py
    ├── parse_thread.py    # File parsing thread
    └── compare_thread.py  # Comparison thread
```

## License

This is a reimplementation of the original dbcCompare tool.
Original copyright (C) 2012 Sava Claudiu Gigel

## Credits

Based on the original dbcCompare application by Sava Claudiu Gigel (csava.dev@gmail.com)
