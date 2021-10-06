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


#\\ Import Modules #############################################################
from krita import *
import math
from PyQt5 import QtWidgets, QtCore, uic
from .photobash_images_modulo import (
    Photobash_Display,
    Photobash_Button,
)

# //
#\\ Global Variables ###########################################################
# //

class PhotobashDocker(DockWidget):
    #\\ Initialize #############################################################
    def __init__(self):
        super().__init__()

        # Construct
        self.setupVariables()
        self.setupInterface()
        self.setupModules()
        self.setStyle()
        self.settingsLoad()

    def setupVariables(self):
        self.mainWidget = QWidget(self)

        self.applicationName = "Photobash"
        self.referencesSetting = "referencesDirectory"
        self.fitCanvasSetting = "fitToCanvas"

        self.currImageScale = 100
        self.fitCanvasChecked = True

        self.imagesButtons = []
        self.foundImages = []

        self.currPage = 0
        self.directoryPath = Application.readSetting(self.applicationName, self.referencesSetting, "")

    def setupInterface(self):
        # Window
        self.setWindowTitle("Photobash Images")

        # Path Name
        self.directoryPlugin = str(
            os.path.dirname(os.path.realpath(__file__)))

        # Photo Bash Docker
        self.window = QWidget()
        self.layout = uic.loadUi(
            self.directoryPlugin + '/photobash_images_docker.ui', self.window)
        self.setWidget(self.window)

        self.layoutButtons = [
            self.layout.imagesButtons0,
            self.layout.imagesButtons1,
            self.layout.imagesButtons2,
            self.layout.imagesButtons3,
            self.layout.imagesButtons4,
            self.layout.imagesButtons5,
            self.layout.imagesButtons6,
            self.layout.imagesButtons7,
            self.layout.imagesButtons8,
        ]

        # Adjust Layouts
        self.layout.imageWidget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.layout.middleWidget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        # setup connections for top elements
        self.layout.filterTextEdit.textChanged.connect(self.updateTextFilter)
        self.layout.changePathButton.clicked.connect(self.changePath)
        # setup connections for bottom elements
        self.layout.previousButton.clicked.connect(lambda: self.updateCurrentPage(-1))
        self.layout.nextButton.clicked.connect(lambda: self.updateCurrentPage(1))
        self.layout.slider.valueChanged.connect(self.updateScale)
        self.layout.fitCanvasCheckBox.stateChanged.connect(self.changedFitCanvas)

    def setupModules(self):
        # Display
        self.imageWidget = Photobash_Display(self.layout.imageWidget)
        self.imageWidget.SIGNAL_HOVER.connect(self.cursorHover)
        self.imageWidget.SIGNAL_CLOSE.connect(self.PB_Display_Close)

        self.imagesButtons = []
        
        for i in range(0, len(self.layoutButtons)):
            layoutButton = self.layoutButtons[i]
            
            imageButton = Photobash_Button(layoutButton)
            # imageButton = layoutButton
            imageButton.SIGNAL_HOVER.connect(self.cursorHover)
            imageButton.SIGNAL_LMB.connect(lambda: self.buttonClick(i))
            # imageButton.SIGNAL_LMB.connect(self.PB_Set_Image)
            imageButton.SIGNAL_WUP.connect(self.PB_Wheel_Up)
            imageButton.SIGNAL_WDN.connect(self.PB_Wheel_Down)
            imageButton.SIGNAL_DISPLAY.connect(self.PB_Display_Open)
            imageButton.SIGNAL_BASH.connect(self.PB_Bash)
            imageButton.SIGNAL_DRAG.connect(self.PB_Drag)

            self.imagesButtons.append(imageButton)

    def setStyle(self):
        self.cursorHover(None)

    # executed whenever the text of the images filter is updated,
    # selects the images that meet the criteria
    def updateTextFilter(self):
        newImages = []
        self.currPage = 0

        if self.directoryPath != "":
            it = QDirIterator(self.directoryPath, QDirIterator.Subdirectories)

            while(it.hasNext()):
                stringsInText = self.layout.filterTextEdit.text().lower().split(" ")

                for word in stringsInText:
                    if word in it.filePath().lower() and (".png" in it.filePath() or ".jpg" in it.filePath() or ".jpeg" in it.filePath()):
                        newImages.append(it.filePath())

                it.next()

            # list of images that match the filter
            if len(self.foundImages) != len(newImages):
                self.foundImages = newImages
                self.updateImages()
            else:
                for i in range(0, len(newImages)):
                    if self.foundImages[i] != newImages[i]:
                        self.foundImages = newImages
                        self.updateImages()
                        return

    # //
    #\\ Bottom Functions #######################################################
    def updateCurrentPage(self, increment):
        if (self.currPage == 0 and increment == -1) or \
            ((self.currPage + 1) * len(self.imagesButtons) > len(self.foundImages) and increment == 1) or \
            len(self.foundImages) == 0:
            return

        self.currPage += increment
        self.updateImages()

    def updateScale(self, value):
        self.currImageScale = value
        self.layout.sliderLabel.setText(f"Image Scale : {self.currImageScale}%")  

    def changedFitCanvas(self, state):
        if state == Qt.Checked:
            self.fitCanvasChecked = True
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "true")
        else:
            self.fitCanvasChecked = False
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "false")

    # //
    #\\ Independant Functions ##################################################
    def clearFocus(self):
        self.layout.filterTextEdit.clearFocus()

    def cursorHover(self, SIGNAL_HOVER):
        # Reset Hover
        bg_alpha = str("background-color: rgba(0, 0, 0, 50); ")
        # Hover Over
        bg_hover = str("background-color: rgba(0, 0, 0, 100); ")

        # Display Image
        self.layout.imageWidget.setStyleSheet(bg_alpha)
        if SIGNAL_HOVER == "D":
            self.layout.imageWidget.setStyleSheet(bg_hover)
        
        # normal images
        for i in range(0, len(self.layoutButtons)):
            self.layoutButtons[i].setStyleSheet(bg_alpha)
                
            if SIGNAL_HOVER == str(i):
                self.layoutButtons[i].setStyleSheet(bg_hover)
        
    def updateImages(self):
        maxWidth = 0
        maxHeight = 0

        buttonsSize = len(self.imagesButtons)

        for i in range(0, buttonsSize):
            if maxWidth < self.imagesButtons[i].width():
                maxWidth = self.imagesButtons[i].width()
            if maxHeight < self.imagesButtons[i].height():
                maxHeight = self.imagesButtons[i].height()

        # don't try to access image that isn't there
        maxRange = min(len(self.foundImages) - self.currPage * buttonsSize, buttonsSize)

        for i in range(0, len(self.imagesButtons)):
            if i < maxRange:
                # image is within valid range, apply it
                path = self.foundImages[i + buttonsSize * self.currPage]
                self.imagesButtons[i].getImage(path)

                #pixmap = QPixmap(self.foundImages[i])
                # icon = QIcon(self.foundImages[i + buttonsSize * self.currPage])

                # self.imagesButtons[i].setIcon(icon)
                # self.imagesButtons[i].setIconSize(QSize(int(maxWidth), int(maxHeight)))

            else:
                # is invalid image, reset
                #self.imagesButtons[i].setIconSize(QSize(0,0))
                pass

        # update text for pagination
        maxNumPage = math.ceil(len(self.foundImages) / len(self.layoutButtons))
        currPage = self.currPage + 1
         
        if maxNumPage == 0: 
            currPage = 0
        # currPage is the index, but we want to present it in a user friendly way, 
        # so it starts at 1
        self.layout.paginationLabel.setText(f"{str(currPage)}/{str(maxNumPage)}")

    def addImageLayer(self, photoPath):
        # Get the document:
        doc = Krita.instance().activeDocument()

        # Saving a non-existent document causes crashes, so lets check for that first.
        if doc is not None:
            root = doc.activeNode().parentNode();

            layerName = photoPath.split("/")[len(photoPath.split("/")) - 1].split(".png")[0].split(".jpg")[0].split(".jpeg")[0]

            tmpLayer = doc.createNode(layerName, "paintLayer")
            newLayer = doc.createFileLayer(layerName, photoPath, "ImageToPPI")

            root.addChildNode(newLayer, None)
            root.addChildNode(tmpLayer, None)

            doc.activeNode().mergeDown()

            activeNode = None

            for node in root.childNodes():
                if node.name() == layerName:
                    activeNode = node

            if self.fitCanvasChecked:
                if activeNode.bounds().width() / activeNode.bounds().height() > doc.bounds().width() / doc.bounds().height():
                    scalingFactor = doc.bounds().width() / activeNode.bounds().width()
                    newWidth = doc.bounds().width() * self.currImageScale / 100
                    newHeight = activeNode.bounds().height() * scalingFactor * self.currImageScale / 100
                else:
                    scalingFactor = doc.bounds().height() / activeNode.bounds().height()
                    newWidth = activeNode.bounds().width() * scalingFactor * self.currImageScale / 100
                    newHeight = doc.bounds().height() * self.currImageScale / 100

                    activeNode.scaleNode(QPoint(activeNode.bounds().center().x(),activeNode.bounds().center().y()), int(newWidth), int(newHeight), "Bicubic")
            else:
                newWidth = activeNode.bounds().width() * self.currImageScale / 100
                newHeight = activeNode.bounds().height() * self.currImageScale / 100

                activeNode.scaleNode(QPoint(activeNode.bounds().center().x(),activeNode.bounds().center().y()), int(newWidth), int(newHeight), "Bicubic")

            # Center image
            offsetX = doc.bounds().width()/2 - activeNode.bounds().center().x()
            offsetY = doc.bounds().height()/2 - activeNode.bounds().center().y()

            activeNode.move(int(offsetX), int(offsetY))

            Krita.instance().activeDocument().refreshProjection()

    def Open_Document(Self, path):
        document = Krita.instance().openDocument(path)
        Application.activeWindow().addView(document)

    # //
    #\\ Signals ################################################################
    def PB_Set_Image(self, SIGNAL_LMB):
        QtCore.qDebug("Image Set")
        if ((self.canvas() is not None) and (self.canvas().view() is not None)):
            pass
        else:
            path = "C:\\Users\\EyeOd\\Desktop\\pink.jpg"
            if path != "":
                try:
                    QtCore.qWarning("Photobash Images - No Document Active > Openning Document")
                    self.Open_Document(path)
                except:
                    pass

    def PB_Wheel_Up(self, SIGNAL_WUP):
        QtCore.qDebug("Wheel Up")
    def PB_Wheel_Down(self, SIGNAL_WDN):
        QtCore.qDebug("Wheel Down")

    def PB_Display_Open(self):
        QtCore.qDebug("Single Open")
        self.imageWidget.getImage(path)
        self.layout.imageWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.middleWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
    def PB_Display_Close(self):
        QtCore.qDebug("Single Close")
        self.layout.imageWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.layout.middleWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def PB_Bash(self):
        QtCore.qDebug("Bash")

    def PB_Drag(self):
        QtCore.qDebug("Drag")

    # //
    #\\ Events #################################################################
    def leaveEvent(self, event):
        self.clearFocus()
        self.settingSave()
    def closeEvent(self, event):
        self.settingSave()

    # //
    #\\ Settings ###############################################################
    def settingsLoad(self):
        pass

    def settingSave(self):
        pass

    # //
    #\\ Canvas Changed #########################################################
    def canvasChanged(self, canvas):
        pass

    # //
    #\\ Notes ##################################################################
    """
    Variables
    Many variables are presented as "var = 0" but then inside the code are reset to "self.var=0" before anything happens it is better to just have them cunstructed with self right away and not worry with a useless variable name.
    I was integrating them inside "def Variables" but I got stuck inside the directory iterator and what it all meant since i never made one before and I dont want to destroy the acctual code.
    Only issues is some  variables names to make it work since they changed considering how I built the UI.

    Initialize
    Source connects to original cycle, Can be deleted after integrated
    Construct connects to new cycle

    def Connect is commented out fllow the trail from here to see what needs to be added

    Top Functions
    Top buttons Triggers

    Bottom Functions
    Bottom buttons triggers

    Signals
    signals that arrive from the modules and trigger something

    Accessing UI element
    self.layout.images_buttons0

    Accessing button Module
    self.imagesButtons0

    sending files to Painter
    path = string with full file path on hardrive
    qimage = QImage(path)
    self.imagesButtons0.getImage(path, qimage)
    """
    # //
    #\\ Source ###########################################################################################################

    def buttonClick(self, position):
        if position < len(self.foundImages) - len(self.imagesButtons) * self.currPage:
            self.addImageLayer(self.foundImages[position + len(self.imagesButtons) * self.currPage])

    def changePath(self):
        fileDialog = QFileDialog(QWidget(self));
        fileDialog.setFileMode(QFileDialog.DirectoryOnly);

        if self.directoryPath == "":
            self.directoryPath = fileDialog.getExistingDirectory(self.mainWidget, "Change Directory for Images", QStandardPaths.writableLocation(QStandardPaths.PicturesLocation))
            Application.writeSetting(self.applicationName, self.referencesSetting, self.directoryPath)
        else:
            self.directoryPath = fileDialog.getExistingDirectory(self.mainWidget, "Change Directory for Images", self.directoryPath)
            Application.writeSetting(self.applicationName, self.referencesSetting, self.directoryPath)

        self.layout.changePathButton.setText("Change References Directory")
        self.updateTextFilter()

    def addImageLayer(self, photoPath):
        # Get the document:
        doc = Krita.instance().activeDocument()

        # Saving a non-existent document causes crashes, so lets check for that first.
        if doc is not None:
            root = doc.activeNode().parentNode();

            layerName = photoPath.split("/")[len(photoPath.split("/")) - 1].split(".png")[0].split(".jpg")[0].split(".jpeg")[0]

            tmpLayer = doc.createNode(layerName, "paintLayer")
            newLayer = doc.createFileLayer(layerName, photoPath, "ImageToPPI")

            root.addChildNode(newLayer, None)
            root.addChildNode(tmpLayer, None)

            doc.activeNode().mergeDown()

            activeNode = None

            for node in root.childNodes():
                if node.name() == layerName:
                    activeNode = node

            if self.fitCanvasChecked:
                if activeNode.bounds().width() / activeNode.bounds().height() > doc.bounds().width() / doc.bounds().height():
                    scalingFactor = doc.bounds().width() / activeNode.bounds().width()
                    newWidth = doc.bounds().width() * self.currImageScale / 100
                    newHeight = activeNode.bounds().height() * scalingFactor * self.currImageScale / 100
                else:
                    scalingFactor = doc.bounds().height() / activeNode.bounds().height()
                    newWidth = activeNode.bounds().width() * scalingFactor * self.currImageScale / 100
                    newHeight = doc.bounds().height() * self.currImageScale / 100

                    activeNode.scaleNode(QPoint(activeNode.bounds().center().x(),activeNode.bounds().center().y()), int(newWidth), int(newHeight), "Bicubic")
            else:
                newWidth = activeNode.bounds().width() * self.currImageScale / 100
                newHeight = activeNode.bounds().height() * self.currImageScale / 100

                activeNode.scaleNode(QPoint(activeNode.bounds().center().x(),activeNode.bounds().center().y()), int(newWidth), int(newHeight), "Bicubic")

            # Center image
            offsetX = doc.bounds().width()/2 - activeNode.bounds().center().x()
            offsetY = doc.bounds().height()/2 - activeNode.bounds().center().y()

            activeNode.move(int(offsetX), int(offsetY))

            Krita.instance().activeDocument().refreshProjection()

    # //
