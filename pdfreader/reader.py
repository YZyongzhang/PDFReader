from collections import OrderedDict

from PySide6.QtCore import QAbstractListModel, QLineF, QModelIndex, QPointF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor, QIcon, QPainter, QPainterPath, QPainterPathStroker, QPen, QPixmap, QPolygonF,
)
from PySide6.QtWidgets import QApplication, QMenu, QWidget


class Pages(QAbstractListModel):
    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self.count = 0
        self.thumbnails = OrderedDict()
        self.marked = set()

    def reload(self, count):
        self.beginResetModel()
        self.count = count
        self.thumbnails.clear()
        self.marked.clear()
        self.endResetModel()

    def set_marked(self, pages):
        changed = self.marked ^ pages
        self.marked = pages
        for page in changed:
            if 0 <= page < self.count:
                index = self.index(page)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else self.count

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.count:
            return None
        page = index.row()
        if role == Qt.ItemDataRole.DisplayRole:
            return f"第 {page + 1} 页" + ("  •" if page in self.marked else "")
        if role == Qt.ItemDataRole.DecorationRole:
            if page not in self.thumbnails:
                points = self.document.pagePointSize(page).toSize()
                if points.isEmpty():
                    return None
                points.scale(QSize(76, 90), Qt.AspectRatioMode.KeepAspectRatio)
                image = self.document.render(page, points)
                self.thumbnails[page] = QIcon(QPixmap.fromImage(image))
                if len(self.thumbnails) > 80:
                    self.thumbnails.popitem(last=False)
            self.thumbnails.move_to_end(page)
            return self.thumbnails[page]
        return None


class PageCanvas(QWidget):
    INK_WIDTH = 2.5
    ERASER_RADIUS = 9

    selection_changed = Signal(bool)
    highlight_requested = Signal()
    translation_requested = Signal()
    note_requested = Signal(object)
    ink_finished = Signal(object)
    ink_erased = Signal(object)
    note_delete_requested = Signal(int)

    def __init__(self, document):
        super().__init__()
        self.document = document
        self.page = -1
        self.scale = 1.0
        self.image = QPixmap()
        self.marks = []
        self.selection = None
        self.start = None
        self.stroke = None
        self.ink_shapes = {}
        self.erased_ink = set()
        self.eraser_position = None
        self.mode = "select"
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setCursor(Qt.CursorShape.IBeamCursor)

    def show_page(self, page, scale):
        if page != self.page:
            self.clear_selection()
            self.reset_gesture()
        self.page = page
        self.scale = scale
        if page < 0:
            self.image = QPixmap()
            self.update()
            return
        points = self.document.pagePointSize(page)
        size = QSize(max(1, round(points.width() * scale)), max(1, round(points.height() * scale)))
        dpi = self.devicePixelRatioF()
        # Cap render resolution while keeping the logical canvas at the selected zoom.
        pixels = size * dpi
        if pixels.width() * pixels.height() > 24_000_000:
            pixels *= (24_000_000 / (pixels.width() * pixels.height())) ** 0.5
        self.image = QPixmap.fromImage(self.document.render(page, pixels))
        self.setFixedSize(size)
        self.update()

    def clear_selection(self):
        self.selection = None
        self.selection_changed.emit(False)
        self.update()

    def set_mode(self, mode):
        self.mode = mode
        self.reset_gesture()
        self.setMouseTracking(mode == "erase")
        self.setCursor(Qt.CursorShape.IBeamCursor if mode == "select" else Qt.CursorShape.CrossCursor)
        self.update()

    def reset_gesture(self):
        self.start = self.stroke = self.eraser_position = None
        self.erased_ink.clear()

    def set_marks(self, marks):
        self.marks = marks
        self.ink_shapes = {
            mark["id"]: self.stroke_outline([QPointF(*p) for p in mark["geometry"]], self.INK_WIDTH)
            for mark in marks if mark["kind"] == "ink" and mark["geometry"]
        }
        self.update()

    def text(self):
        return self.selection.text().strip() if self.selection else ""

    def selection_geometry(self):
        return [[[point.x(), point.y()] for point in polygon] for polygon in self.selection.bounds()]

    def point_at(self, position):
        bounds = self.document.pagePointSize(self.page)
        return QPointF(
            min(bounds.width(), max(0, position.x() / self.scale)),
            min(bounds.height(), max(0, position.y() / self.scale)),
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        if self.page < 0:
            return
        painter.drawPixmap(self.rect(), self.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.scale(self.scale, self.scale)
        for mark in self.marks:
            points = mark["geometry"]
            if mark["kind"] == "highlight":
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(250, 194, 60, 100))
                for polygon in points:
                    painter.drawPolygon(QPolygonF([QPointF(*point) for point in polygon]))
            elif mark["kind"] == "ink":
                if mark["id"] not in self.erased_ink and mark["id"] in self.ink_shapes:
                    painter.fillPath(self.ink_shapes[mark["id"]], QColor("#7650c9"))
            elif points:
                painter.setPen(QPen(QColor("#ffffff"), 1.4))
                painter.setBrush(QColor("#7352cc"))
                painter.drawEllipse(QPointF(*points[0]), 6, 6)
        if self.stroke:
            self.paint_stroke(painter, self.stroke)
        if self.selection:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(101, 70, 217, 83))
            for polygon in self.selection.bounds():
                painter.drawPolygon(polygon)
        if self.eraser_position is not None:
            radius = self.ERASER_RADIUS / self.scale
            pen = QPen(QColor("#6246ca"), 1.5)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.setBrush(QColor(98, 70, 202, 30))
            painter.drawEllipse(self.eraser_position, radius, radius)

    @staticmethod
    def stroke_outline(points, width):
        path = QPainterPath(points[0])
        for point in points[1:]:
            path.lineTo(point)
        if path.isEmpty():
            path.addEllipse(points[0], width / 2, width / 2)
            return path
        stroker = QPainterPathStroker()
        stroker.setWidth(width)
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return stroker.createStroke(path)

    def paint_stroke(self, painter, points):
        painter.setPen(QPen(QColor("#7650c9"), self.INK_WIDTH, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        if len(points) == 1:
            painter.drawPoint(points[0])
        else:
            painter.drawPolyline(QPolygonF(points))

    def mousePressEvent(self, event):
        if self.page < 0 or event.button() != Qt.MouseButton.LeftButton:
            return
        point = self.point_at(event.position())
        if self.mode == "note":
            self.note_requested.emit(point)
            return
        self.clear_selection()
        self.start = point
        if self.mode == "erase":
            self.erase_to(point)
            self.update()
        if self.mode == "ink":
            self.stroke = [point]
            self.update()

    def mouseMoveEvent(self, event):
        if self.page < 0:
            return
        point = self.point_at(event.position())
        if self.mode == "erase":
            self.eraser_position = point
            if self.start is not None:
                self.erase_to(point)
        elif self.start is None:
            return
        elif self.stroke is not None:
            if point != self.stroke[-1]:
                self.stroke.append(point)
        else:
            self.find_selection(point)
        self.update()

    def erase_to(self, point):
        swept = self.stroke_outline([self.start, point], 2 * self.ERASER_RADIUS / self.scale)
        self.erased_ink.update(
            mark for mark, shape in self.ink_shapes.items()
            if mark not in self.erased_ink and swept.intersects(shape)
        )
        self.eraser_position = self.start = point

    def leaveEvent(self, event):
        self.eraser_position = None
        self.update()
        super().leaveEvent(event)

    def find_selection(self, point):
        if (point - self.start).manhattanLength() * self.scale < 3:
            self.clear_selection()
            return
        selection = self.document.getSelection(self.page, self.start, point)
        self.selection = selection if selection.isValid() and selection.text().strip() else None
        self.selection_changed.emit(self.selection is not None)

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self.start is None:
            return
        point = self.point_at(event.position())
        if self.mode == "erase":
            self.erase_to(point)
            erased = self.erased_ink.copy()
            self.erased_ink.clear()
            if erased:
                self.ink_erased.emit(erased)
        elif self.stroke is not None:
            if point != self.stroke[-1]:
                self.stroke.append(point)
            stroke = [[p.x(), p.y()] for p in self.stroke]
            self.stroke = None
            self.ink_finished.emit(stroke)
        else:
            self.find_selection(point)
        self.start = None
        self.update()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        if self.text():
            menu.addAction("翻译选中文本", self.translation_requested.emit)
            menu.addAction("高亮选中文本", self.highlight_requested.emit)
            menu.addAction("复制选中文本", lambda: QApplication.clipboard().setText(self.text()))
        if self.page >= 0:
            point = self.point_at(event.pos())
            menu.addAction("在此添加批注", lambda: self.note_requested.emit(point))
            for mark in reversed(self.marks):
                if (mark["kind"] == "note" and mark["geometry"]
                        and QLineF(point, QPointF(*mark["geometry"][0])).length() <= 8):
                    menu.addAction("删除此批注", lambda: self.note_delete_requested.emit(mark["id"]))
                    break
        if not menu.isEmpty():
            menu.exec(event.globalPos())
