from math import ceil

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCursor, QTextDocument, QTextFormat, QTextOption
from PySide6.QtWidgets import QSizePolicy, QTextBrowser


class MarkdownMessage(QTextBrowser):
    def __init__(self, text):
        super().__init__()
        self.setObjectName("markdownMessage")
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        document = self.document()
        document.setDocumentMargin(1)
        document.setIndentWidth(22)
        document.setMarkdown(
            text,
            QTextDocument.MarkdownFeature.MarkdownDialectGitHub
            | QTextDocument.MarkdownFeature.MarkdownNoHTML,
        )
        self.style_code_blocks()
        document.documentLayout().documentSizeChanged.connect(self.fit_height)
        self.horizontalScrollBar().rangeChanged.connect(self.fit_height)
        self.fit_height()

    def style_code_blocks(self):
        cursor = QTextCursor(self.document())
        cursor.beginEditBlock()
        block = self.document().firstBlock()
        while block.isValid():
            formatting = block.blockFormat()
            if formatting.hasProperty(QTextFormat.Property.BlockCodeFence):
                formatting.setBackground(QColor("#f1edf9"))
                formatting.setLeftMargin(6)
                formatting.setRightMargin(6)
                cursor.setPosition(block.position())
                cursor.setBlockFormat(formatting)
            block = block.next()
        cursor.endEditBlock()

    def fit_height(self, *_):
        bar = self.horizontalScrollBar()
        extra = bar.sizeHint().height() if bar.maximum() > 0 else 0
        height = ceil(self.document().size().height()) + extra + 2 * self.frameWidth()
        if height != self.minimumHeight():
            self.setFixedHeight(height)

    def loadResource(self, resource_type, name):
        return None

    def wheelEvent(self, event):
        # The surrounding conversation owns the vertical scroll.
        event.ignore()
