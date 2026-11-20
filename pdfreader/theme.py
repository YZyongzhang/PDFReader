STYLE = """
QWidget { color: #253044; font-size: 14px; }
QMainWindow, QDialog, QMessageBox { background: #fafbfe; }
QFrame#topbar { background: #ffffff; border-bottom: 1px solid #e3e7f0; }
QFrame#sidebar { background: #fafbfe; }
QFrame#assistant, QWidget#messages { background: #f7f6fc; }
QFrame#toolbar, QFrame#footer { background: #f8f9fd; }
QFrame#toolbar { border-bottom: 1px solid #e2e6ef; }
QFrame#footer { border-top: 1px solid #e2e6ef; }
QFrame#reading { background: #e9ecf4; }
QFrame#composer { background: #fff; border: 1px solid #dcd7ee; border-radius: 12px; }
QLabel#brandBadge, QLabel#emptyBadge {
    background: #6246ca; color: white; border-radius: 10px; font-weight: 700;
}
QLabel#emptyBadge { background: #e2dbf9; color: #5439bd; font-size: 19px; }
QLabel#brand { font-size: 19px; font-weight: 700; color: #20283b; }
QLabel#heading { font-size: 17px; font-weight: 700; }
QLabel#dialogTitle, QLabel#emptyTitle { font-size: 23px; font-weight: 700; }
QLabel#muted { color: #59657d; font-size: 13px; }
QLabel#assistantBadge {
    background: #ebe4ff; color: #5031b0; border-radius: 11px; font-size: 13px; font-weight: 700;
}
QLabel#messageRole { font-size: 13px; font-weight: 700; color: #5e4aa6; }
QFrame#userMessage { background: #ebe4ff; border: 1px solid #e1d6fc; border-radius: 12px; }
QFrame#aiMessage { background: #fff; border: 1px solid #e2ddef; border-radius: 12px; }
QLabel#messageBody { color: #253044; }
QPushButton {
    background: #fff; border: 1px solid #dce1ed; border-radius: 7px;
    padding: 5px 10px; min-height: 22px;
}
QPushButton:hover { background: #f2eeff; border-color: #c8b9f1; }
QPushButton:focus, QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #8c78d9;
}
QPushButton:checked { background: #ece6fc; color: #5032af; border-color: #c5b6ef; }
QPushButton:disabled { background: #f4f5f9; color: #778197; border-color: #e7e9f0; }
QPushButton#primary { background: #6246ca; color: #fff; border-color: #6246ca; font-weight: 600; }
QPushButton#primary:hover { background: #5136b6; }
QPushButton#primary:disabled { background: #ded8f3; color: #5f527c; border-color: #ded8f3; }
QPushButton#quietButton {
    background: transparent; color: #66548e; border: 1px solid transparent;
    padding: 1px 6px; min-height: 20px; font-size: 13px;
}
QPushButton#quietButton:hover { background: #ece6fa; }
QPushButton#quietButton:focus { border-color: #8c78d9; }
QPushButton#quietButton:disabled { color: #7a768a; }
QPushButton#danger:enabled { color: #9f244b; }
QPushButton#danger:hover { background: #fff0f5; border-color: #e7becd; }
QListView, QListWidget, QLineEdit, QComboBox, QSpinBox, QTextEdit, QTextBrowser {
    background: #fff; border: 1px solid #dfe3ef; border-radius: 7px; padding: 5px;
    selection-background-color: #ebe5fc; selection-color: #41317e;
}
QTextBrowser#markdownMessage, QTextEdit#composerInput {
    background: #fff; border: 0; border-radius: 0; padding: 0;
}
QTextEdit#composerInput:focus { border: 0; }
QListView::item { padding: 6px; border-radius: 5px; }
QListView::item:selected { background: #ede8fc; color: #4b329b; }
QListView::item:hover:!selected { background: #f3f4fa; }
QTabWidget::pane { border: 0; }
QTabBar::tab { color: #606c84; padding: 8px 13px; border-bottom: 2px solid #e7eaf2; }
QTabBar::tab:selected { color: #5438ba; border-bottom: 2px solid #7255d3; font-weight: 700; }
QScrollArea { background: transparent; border: 0; }
QWidget#paperDeck { background: #e9ecf4; }
QSplitter::handle { background: #dfe3ee; }
QSplitter::handle:hover { background: #ad9be6; }
QToolTip { background: #2c2540; color: #fff; border: 0; padding: 4px; }
"""
