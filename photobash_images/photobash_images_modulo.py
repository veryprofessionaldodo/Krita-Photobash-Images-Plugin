# Photobash Images is a Krita plugin to get CC0 images based on a search,
# straight from the Krita Interface. Useful for textures and concept art!
# Copyright (C) 2020  Pedro Reis.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from krita import *
from PyQt5 import QtWidgets, QtCore


class Photobash_Display(QWidget):
    SIGNAL_HOVER = QtCore.pyqtSignal(str)
    SIGNAL_CLOSE = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        # QImage
        self.path = ""
        self.qimage = QImage(self.path)
        self.pixmap = QPixmap(50, 50).fromImage(self.qimage)

    def sizeHint(self):
        return QtCore.QSize(5000,5000)

    def enterEvent(self, event):
        self.SIGNAL_HOVER.emit("D")
    def leaveEvent(self, event):
        self.SIGNAL_HOVER.emit("None")

    def mousePressEvent(self, event):
        if (event.modifiers() == QtCore.Qt.ShiftModifier or event.modifiers() == QtCore.Qt.ControlModifier or event.modifiers() == QtCore.Qt.AltModifier):
            self.SIGNAL_CLOSE.emit(0)

    def mouseDoubleClickEvent(self, event):
        self.SIGNAL_CLOSE.emit(0)

    def mouseMoveEvent(self, event):
        if (event.modifiers() == QtCore.Qt.ShiftModifier or event.modifiers() == QtCore.Qt.ControlModifier or event.modifiers() == QtCore.Qt.AltModifier):
            # MimeData
            mimedata = QMimeData()
            url = QUrl().fromLocalFile(self.path)
            mimedata.setUrls([url])
            mimedata.setImageData(self.qimage)
            # Clipboard
            clipboard = QApplication.clipboard().setImage(self.qimage)
            # Drag
            drag = QDrag(self)
            drag.setMimeData(mimedata)
            drag.setPixmap(self.pixmap)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def Input_Image(self, path, qimage):
        self.path = path
        self.qimage = qimage
        self.pixmap = QPixmap(50, 50).fromImage(qimage)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen)
        # Calculations
        total_width = event.rect().width()
        total_height = event.rect().height()
        image_width = self.qimage.width()
        image_height = self.qimage.height()
        try:
            var_w = total_width / image_width
            var_h = total_height / image_height
        except:
            var_w = 1
            var_h = 1
        size = 0
        if var_w <= var_h:
            size = var_w
        if var_w > var_h:
            size = var_h
        wt2 = total_width * 0.5
        ht2 = total_height * 0.5
        self.scaled_width = image_width * size
        self.scaled_height = image_height * size
        offset_x = wt2 - (self.scaled_width * 0.5)
        offset_y = ht2 - (self.scaled_height * 0.5)
        # Save State for Painter
        painter.save()
        # QImag
        image = self.qimage
        painter.translate(offset_x, offset_y)
        painter.scale(size, size)
        painter.drawImage(0,0,image)
        # Restore Space
        painter.restore()

class Photobash_Button(QWidget):
    SIGNAL_HOVER = QtCore.pyqtSignal(str)
    SIGNAL_LMB = QtCore.pyqtSignal(int)
    SIGNAL_WUP = QtCore.pyqtSignal(int)
    SIGNAL_WDN = QtCore.pyqtSignal(int)
    SIGNAL_DISPLAY = QtCore.pyqtSignal(int)
    SIGNAL_BASH = QtCore.pyqtSignal(int)
    SIGNAL_DRAG = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__()
        # Variables
        self.number = None
        # QImage
        self.path = ""
        self.qimage = QImage(self.path)
        self.pixmap = QPixmap(50, 50).fromImage(self.qimage)
        self.scaled_width = 1
        self.scaled_height = 1
    def sizeHint(self):
        return QtCore.QSize(2000,2000)

    def Number(self, number):
        self.number = number
    def enterEvent(self, event):
        self.SIGNAL_HOVER.emit(str(self.number))
    def leaveEvent(self, event):
        self.SIGNAL_HOVER.emit("None")

    def mousePressEvent(self, event):
        if (event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton):
            self.SIGNAL_LMB.emit(self.number)
    def mouseMoveEvent(self, event):
        if (event.modifiers() == QtCore.Qt.ShiftModifier or event.modifiers() == QtCore.Qt.ControlModifier or event.modifiers() == QtCore.Qt.AltModifier):
            # MimeData
            mimedata = QMimeData()
            url = QUrl().fromLocalFile(self.path)
            mimedata.setUrls([url])
            mimedata.setImageData(self.qimage)
            # Clipboard
            clipboard = QApplication.clipboard().setImage(self.qimage)
            # Drag
            drag = QDrag(self)
            drag.setMimeData(mimedata)
            drag.setPixmap(self.pixmap)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def wheelEvent(self,event):
        delta = event.angleDelta()
        if delta.y() > 60:
            self.SIGNAL_WUP.emit(0)
        elif delta.y() < -60:
            self.SIGNAL_WDN.emit(0)

    def contextMenuEvent(self, event): # Right Click
        cmenu = QMenu(self)
        cmenu_display = cmenu.addAction("Display")
        cmenu_bash = cmenu.addAction("Bash")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == cmenu_display:
            self.SIGNAL_DISPLAY.emit(0)
        if action == cmenu_bash:
            self.SIGNAL_BASH.emit(0)

    def Input_Image(self, path, qimage):
        self.path = path
        self.qimage = qimage
        self.pixmap = QPixmap(50, 50).fromImage(qimage)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen)
        # Calculations
        total_width = event.rect().width()
        total_height = event.rect().height()
        image_width = self.qimage.width()
        image_height = self.qimage.height()
        try:
            var_w = total_width / image_width
            var_h = total_height / image_height
        except:
            var_w = 1
            var_h = 1
        size = 0
        if var_w <= var_h:
            size = var_w
        if var_w > var_h:
            size = var_h
        wt2 = total_width * 0.5
        ht2 = total_height * 0.5
        self.scaled_width = image_width * size
        self.scaled_height = image_height * size
        offset_x = wt2 - (self.scaled_width * 0.5)
        offset_y = ht2 - (self.scaled_height * 0.5)
        # Save State for Painter
        painter.save()
        # QImag
        image = self.qimage
        painter.translate(offset_x, offset_y)
        painter.scale(size, size)
        painter.drawImage(0,0,image)
        # Restore Space
        painter.restore()
