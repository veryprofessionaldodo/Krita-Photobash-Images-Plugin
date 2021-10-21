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

DRAG_DELTA = 30

def customPaintEvent(instance, event):
    painter = QPainter(instance)
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
    painter.setPen(QtCore.Qt.NoPen)

    # Calculations
    total_width = event.rect().width()
    total_height = event.rect().height()
    image_width = instance.qimage.width()
    image_height = instance.qimage.height()

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

    instance.scaled_width = image_width * size
    instance.scaled_height = image_height * size

    offset_x = wt2 - (instance.scaled_width * 0.5)
    offset_y = ht2 - (instance.scaled_height * 0.5)

    # Save State for Painter
    painter.save()
    painter.translate(offset_x, offset_y)
    painter.scale(size, size)
    painter.drawImage(0,0,instance.qimage)

    # Restore Space
    painter.restore()

def customSetImage(instance, image):
    instance.qimage = QImage() if image is None else image
    instance.pixmap = QPixmap(50, 50).fromImage(instance.qimage)

    instance.update()

def customMouseMoveEvent(self, event):
    if event.modifiers() != QtCore.Qt.ShiftModifier and event.modifiers() != QtCore.Qt.ControlModifier and event.modifiers() != QtCore.Qt.AltModifier:
        self.PREVIOUS_DRAG_X = None
        return 

    # alt modifier is reserved for scrolling through
    if self.PREVIOUS_DRAG_X and event.modifiers() == QtCore.Qt.AltModifier:
        diffX = event.x() - self.PREVIOUS_DRAG_X

        if self.PREVIOUS_DRAG_X < event.x() - DRAG_DELTA:
            self.SIGNAL_WUP.emit(0)
            self.PREVIOUS_DRAG_X = event.x()
        elif self.PREVIOUS_DRAG_X > event.x() + DRAG_DELTA:
            self.SIGNAL_WDN.emit(0)
            self.PREVIOUS_DRAG_X = event.x()

        return 

    # MimeData
    mimedata = QMimeData()
    url = QUrl().fromLocalFile(self.path)
    mimedata.setUrls([url])
    mimedata.setImageData(self.pixmap)

    # Clipboard
    QApplication.clipboard().setImage(self.qimage)

    # Drag
    drag = QDrag(self)
    drag.setMimeData(mimedata)
    drag.setPixmap(self.pixmap)
    drag.setHotSpot(event.pos())
    drag.exec_(Qt.CopyAction)

class Photobash_Display(QWidget):
    SIGNAL_HOVER = QtCore.pyqtSignal(str)
    SIGNAL_CLOSE = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super(Photobash_Display, self).__init__(parent)
        customSetImage(self, None)

    def sizeHint(self):
        return QtCore.QSize(5000,5000)

    def enterEvent(self, event):
        self.SIGNAL_HOVER.emit("D")

    def leaveEvent(self, event):
        self.SIGNAL_HOVER.emit("None")

    def mousePressEvent(self, event):
        if (event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton):
            self.SIGNAL_CLOSE.emit(0)

    def mouseMoveEvent(self, event):
        customMouseMoveEvent(self, event)

    def setImage(self, path, image):
        self.path = path
        customSetImage(self, image)

    def paintEvent(self, event):
        customPaintEvent(self, event)

class Photobash_Button(QWidget):
    SIGNAL_HOVER = QtCore.pyqtSignal(str)
    SIGNAL_LMB = QtCore.pyqtSignal(int)
    SIGNAL_WUP = QtCore.pyqtSignal(int)
    SIGNAL_WDN = QtCore.pyqtSignal(int)
    SIGNAL_PREVIEW = QtCore.pyqtSignal(str)
    SIGNAL_FAVOURITE = QtCore.pyqtSignal(str)
    SIGNAL_OPEN_NEW = QtCore.pyqtSignal(str)
    SIGNAL_REFERENCE = QtCore.pyqtSignal(str)
    SIGNAL_DRAG = QtCore.pyqtSignal(int)
    PREVIOUS_DRAG_X = None

    def __init__(self, parent):
        super(Photobash_Button, self).__init__(parent)
        # Variables
        self.number = -1
        # QImage
        customSetImage(self, None)

        self.scaled_width = 1
        self.scaled_height = 1

    def setNumber(self, number):
        self.number = number

    def sizeHint(self):
        return QtCore.QSize(2000,2000)

    def enterEvent(self, event):
        self.SIGNAL_HOVER.emit(str(self.number))

    def leaveEvent(self, event):
        self.SIGNAL_HOVER.emit("None")

    def mousePressEvent(self, event):
        if event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton:
            self.SIGNAL_LMB.emit(self.number)
        if event.modifiers() == QtCore.Qt.AltModifier:
            self.PREVIOUS_DRAG_X = event.x()

    def mouseDoubleClickEvent(self, event):
        # Prevent double click to open the same image twice
        pass

    def mouseMoveEvent(self, event):
        customMouseMoveEvent(self, event)

    def wheelEvent(self,event):
        delta = event.angleDelta()
        if delta.y() > 20:
            self.SIGNAL_WUP.emit(0)
        elif delta.y() < -20:
            self.SIGNAL_WDN.emit(0)

    # menu opened with right click
    def contextMenuEvent(self, event):
        cmenu = QMenu(self)
        cmenuDisplay = cmenu.addAction("Preview In Docker")
        cmenuFavourite = cmenu.addAction("Pin To Beginning")
        cmenuOpenNew = cmenu.addAction("Open as New Document")
        cmenuReference = cmenu.addAction("Place as Reference")

        background = qApp.palette().color(QPalette.Window).name().split("#")[1]
        cmenuStyleSheet = f"""QMenu {{ background-color: #AA{background}; border: 1px solid #{background}; }}"""
        cmenu.setStyleSheet(cmenuStyleSheet)

        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == cmenuDisplay:
            self.SIGNAL_PREVIEW.emit(self.path)
        if action == cmenuFavourite:
            self.SIGNAL_FAVOURITE.emit(self.path)
        if action == cmenuOpenNew:
            self.SIGNAL_OPEN_NEW.emit(self.path)
        if action == cmenuReference:
            self.SIGNAL_REFERENCE.emit(self.path)

    def setImage(self, path, image):
        self.path = path
        customSetImage(self, image)

    def paintEvent(self, event):
        customPaintEvent(self, event)
