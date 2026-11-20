import sqlite3
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication, QMessageBox

from .store import Store
from .theme import STYLE
from .window import ReaderWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDFReader")
    app.setApplicationDisplayName("页间")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    directory = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    try:
        store = Store(Path(directory))
    except (OSError, sqlite3.Error) as error:
        QMessageBox.critical(None, "无法打开文档库", str(error))
        return 1
    window = ReaderWindow(store)
    if len(sys.argv) > 1:
        window.import_files(sys.argv[1:])
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
