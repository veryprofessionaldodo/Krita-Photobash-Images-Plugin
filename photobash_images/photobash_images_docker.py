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
from PyQt5 import QtWidgets, QtCore, uic
import math
from .photobash_images_modulo import (
    Photobash_Display,
    Photobash_Button,
    )
#//
#\\ Global Variables ###########################################################
#//

class PhotobashDocker(DockWidget):
    applicationName = "Photobash"
    referencesSetting = "referencesDirectory"
    fitCanvasSetting = "fitToCanvas"

    # foundImages = []

    # directoryPath = ""
    # currPage = 0
    currImageScale = 100
    fitCanvasChecked = True

    filterTextEdit = None
    mainWidget = None
    changePathButton = None
    sliderLabel = None
    imagesButtons = []

    #\\ Initialize #############################################################
    def __init__(self):
        super(PhotobashDocker, self).__init__()

        # # Source
        # self.Default()

        # Construct
        self.Variables()
        self.User_interface()
        self.Modules()
        self.Setup()
        self.Connect()
        self.Style()
        self.Settings_Load()

    def Variables(self):
        self.foundImages = []

        self.currPage = 0
        self.directoryPath = ""

        self.qimage_display = QImage()
        self.qimage_button = QImage()
        self.numImages = 9

    def User_interface(self):
        # Window
        self.setWindowTitle("Photobash Images")
        # Path Name
        self.directoryPlugin = str(os.path.dirname(os.path.realpath(__file__)))
        # Photo Bash Docker
        self.window = QWidget()
        self.layout = uic.loadUi(self.directoryPlugin + '/photobash_images_docker.ui', self.window)
        self.setWidget(self.window)
        # Adjust Layouts
        self.layout.imageWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.layout.middleWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def Modules(self):
        # Display
        self.imageWidget = Photobash_Display(self.layout.imageWidget)
        self.imageWidget.SIGNAL_HOVER.connect(self.Cursor_Hover)
        self.imageWidget.SIGNAL_CLOSE.connect(self.PB_Display_Close)

        self.imagesButtons = []

        for i in range(0, self.numImages):
            button = "imagesButtons" + str(i)

            imageButton = Photobash_Button(self.layout[button])
            imageButton.SIGNAL_HOVER.connect(self.Cursor_Hover)
            imageButton.SIGNAL_LMB.connect(self.PB_Set_Image)
            imageButton.SIGNAL_WUP.connect(self.PB_Wheel_Up)
            imageButton.SIGNAL_WDN.connect(self.PB_Wheel_Down)
            imageButton.SIGNAL_DISPLAY.connect(self.PB_Display_Open)
            imageButton.SIGNAL_BASH.connect(self.PB_Bash)
            imageButton.SIGNAL_DRAG.connect(self.PB_Drag)

    def Setup(self):
        pass
    def Connect(self):
        # UI Top
        # self.layout.filterTextEdit.textChanged.connect(self.Update_Text_Filter)
        self.layout.changePathButton.clicked.connect(self.Change_Path)
        # UI Bottom
        # self.layout.previousButton.clicked.connect(lambda: self.Update_Current_Page(-1))
        # self.layout.nextButton.clicked.connect(lambda: self.Update_Current_Page(1))
        # self.layout.slider.valueChanged.connect(self.Update_Scale)
        # self.layout.fitCanvasCheckBox.stateChanged.connect(self.Changed_Fit_Canvas)
    def Style(self):
        self.Cursor_Hover(None)

    #//
    #\\ Top Functions ##########################################################
    def Update_Text_Filter(self):
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

            if len(self.foundImages) != len(newImages):
                self.foundImages = newImages
                self.Update_Images()
            else:
                for i in range(0, len(newImages)):
                    if self.foundImages[i] != newImages[i]:
                        self.foundImages = newImages
                        self.Update_Images()
                        return

    def Change_Path(self):
        fileDialog = QFileDialog(QWidget(self))
        fileDialog.setFileMode(QFileDialog.DirectoryOnly)

        if self.directoryPath == "":
            self.directoryPath = fileDialog.getExistingDirectory(self.mainWidget, "Change Directory for Images", QStandardPaths.writableLocation(QStandardPaths.PicturesLocation))
            Application.writeSetting(self.applicationName, self.referencesSetting, self.directoryPath)
        else:
            self.directoryPath = fileDialog.getExistingDirectory(self.mainWidget, "Change Directory for Images", self.directoryPath)
            Application.writeSetting(self.applicationName, self.referencesSetting, self.directoryPath)

        self.layout.changePathButton.setText("Change References Directory")
        self.Update_Text_Filter()

    #//
    #\\ Bottom Functions #######################################################
    def Update_Current_Page(self, increment):
        if (self.currPage == 0 and increment == -1) or \
            ((self.currPage + 1) * len(self.imagesButtons) > len(self.foundImages) and increment == 1) or \
            len(self.foundImages) == 0:
            return

        self.currPage += increment
        self.Update_Images()

    def Update_Scale(self, value):
        self.currImageScale = value
        self.sliderLabel.setText(f"Image Scale : {self.currImageScale}%")

    def Changed_Fit_Canvas(self, state):
        if state == Qt.Checked:
            self.fitCanvasChecked = True
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "true")
        else:
            self.fitCanvasChecked = False
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "false")

    #//
    #\\ Independant Functions ##################################################
    def Clear_Focus(self):
        self.layout.filterTextEdit.clearFocus()

    def Cursor_Hover(self, SIGNAL_HOVER):
        # Reset Hover
        bg_alpha = str("background-color: rgba(0, 0, 0, 50); ")
        self.layout.imageWidget.setStyleSheet(bg_alpha)
        self.layout.imagesButtons0.setStyleSheet(bg_alpha)
        self.layout.imagesButtons1.setStyleSheet(bg_alpha)
        self.layout.imagesButtons2.setStyleSheet(bg_alpha)
        self.layout.imagesButtons3.setStyleSheet(bg_alpha)
        self.layout.imagesButtons4.setStyleSheet(bg_alpha)
        self.layout.imagesButtons5.setStyleSheet(bg_alpha)
        self.layout.imagesButtons6.setStyleSheet(bg_alpha)
        self.layout.imagesButtons7.setStyleSheet(bg_alpha)
        self.layout.imagesButtons8.setStyleSheet(bg_alpha)
        # Hover Over
        bg_hover = str("background-color: rgba(0, 0, 0, 100); ")
        if SIGNAL_HOVER == "D":
            self.layout.imageWidget.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "0":
            self.layout.imagesButtons0.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "1":
            self.layout.imagesButtons1.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "2":
            self.layout.imagesButtons2.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "3":
            self.layout.imagesButtons3.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "4":
            self.layout.imagesButtons4.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "5":
            self.layout.imagesButtons5.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "6":
            self.layout.imagesButtons6.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "7":
            self.layout.imagesButtons7.setStyleSheet(bg_hover)
        if SIGNAL_HOVER == "8":
            self.layout.imagesButtons8.setStyleSheet(bg_hover)

    def Update_Images(self):
        maxWidth = 0
        maxHeight = 0

        buttonsSize = len(self.imagesButtons)

        for i in range(0, buttonsSize):
            if maxWidth < self.imagesButtons[i].width():
                maxWidth = self.imagesButtons[i].width()
            if maxHeight < self.imagesButtons[i].height():
                maxHeight = self.imagesButtons[i].height()

        maxRange = min(len(self.foundImages) - self.currPage * buttonsSize, buttonsSize)

        for i in range(0, len(self.imagesButtons)):
            if i < maxRange:
                # imagesButtons[i].Input_Image(path, QImage(path))

                icon = QIcon(self.foundImages[i + buttonsSize * self.currPage])

                self.imagesButtons[i].setIcon(icon)
                self.imagesButtons[i].setIconSize(QSize(int(maxWidth), int(maxHeight)))
            else:
                self.imagesButtons[i].setIconSize(QSize(0,0))

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

    #//
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
        # self.imageWidget.Input_Image(path, QImage(path))
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

    #//
    #\\ Events #################################################################
    def leaveEvent(self, event):
        self.Clear_Focus()
        self.Settings_Save()
    def closeEvent(self, event):
        self.Settings_Save()

    #//
    #\\ Settings ###############################################################
    def Settings_Load(self):
        pass
    def Settings_Save(self):
        pass

    #//
    #\\ Canvas Changed #########################################################
    def canvasChanged(self, canvas):
        pass

    #//
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
    self.layout.imagesButtons0

    Accessing button Module
    self.imagesButtons0

    sending files to Painter
    path = string with full file path on hardrive
    qimage = QImage(path)
    self.imagesButtons0.Input_Image(path, qimage)
    """
    #//



    #\\ Source ###########################################################################################################
    def Default(self):
        # Read settings
        self.directoryPath = Application.readSetting(self.applicationName, self.referencesSetting, "")

        if Application.readSetting(self.applicationName, self.fitCanvasSetting, "true") == "true":
            self.fitCanvasChecked = True
        else:
            self.fitCanvasChecked = False

        self.currImageScale = 100

        self.setLayout()

    def setLayout(self):
        self.mainWidget = QWidget(self)
        self.setWidget(self.mainWidget)

        # Filtering text
        self.filterTextEdit = QLineEdit(self.mainWidget)
        self.filterTextEdit.setPlaceholderText("Filter images by words...")
        self.filterTextEdit.textChanged.connect(self.updateTextFilter)

        if self.directoryPath != "":
            self.changePathButton = QPushButton("Change References Directory", self.mainWidget)
        else:
            self.changePathButton = QPushButton("Set References Directory", self.mainWidget)

        self.changePathButton.clicked.connect(self.changePath)

        mainLayout = QVBoxLayout()

        topLayout = QHBoxLayout()
        topLayout.addWidget(self.filterTextEdit)
        topLayout.addWidget(self.changePathButton)

        imagesLayout = QVBoxLayout()

        for i in range(0,3):
            rowLayout = QHBoxLayout()

            for j in range(0,3):
                button = QToolButton(self.mainWidget)
                button.setMaximumHeight(3000)
                button.setMaximumWidth(3000)
                button.setMinimumHeight(self.mainWidget.height() / 3)
                button.setMinimumWidth(self.mainWidget.width() / 3)

                self.imagesButtons.append(button)

                rowLayout.addWidget(button)

            imagesLayout.addLayout(rowLayout)

        self.imagesButtons[0].clicked.connect(lambda: self.buttonClick(0))
        self.imagesButtons[1].clicked.connect(lambda: self.buttonClick(1))
        self.imagesButtons[2].clicked.connect(lambda: self.buttonClick(2))
        self.imagesButtons[3].clicked.connect(lambda: self.buttonClick(3))
        self.imagesButtons[4].clicked.connect(lambda: self.buttonClick(4))
        self.imagesButtons[5].clicked.connect(lambda: self.buttonClick(5))
        self.imagesButtons[6].clicked.connect(lambda: self.buttonClick(6))
        self.imagesButtons[7].clicked.connect(lambda: self.buttonClick(7))
        self.imagesButtons[8].clicked.connect(lambda: self.buttonClick(8))

        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(imagesLayout)

        bottomLayout = QHBoxLayout()
        previousButton = QToolButton(self.mainWidget)
        previousButton.setMaximumWidth(3000)
        previousButton.clicked.connect(lambda: self.updateCurrPage(-1))
        previousButton.setArrowType(Qt.ArrowType.LeftArrow)

        nextButton = QToolButton(self.mainWidget)
        nextButton.setMaximumWidth(3000)
        nextButton.clicked.connect(lambda: self.updateCurrPage(1))
        nextButton.setArrowType(Qt.ArrowType.RightArrow)

        self.sliderLabel = QLabel(self.mainWidget)
        self.sliderLabel.setText(f"Scale : {self.currImageScale}%")
        self.sliderLabel.setMaximumWidth(self.sliderLabel.fontMetrics().width(self.sliderLabel.text()))

        slider = QSlider(Qt.Horizontal, self)
        slider.setValue(self.currImageScale)
        slider.setMaximum(100)
        slider.setMinimum(10)
        slider.setMaximumWidth(3000)
        slider.valueChanged.connect(self.updateScale)

        fitBordersLabel = QLabel(self.mainWidget)
        fitBordersLabel.setText("Fit Canvas")
        fitBordersLabel.setMaximumWidth(fitBordersLabel.fontMetrics().width(fitBordersLabel.text()))

        fitCanvasCheckBox = QCheckBox(self.mainWidget)
        fitCanvasCheckBox.setCheckState(self.fitCanvasChecked)
        fitCanvasCheckBox.stateChanged.connect(self.changedFitCanvas)
        fitCanvasCheckBox.setTristate(False)

        bottomLayout.addWidget(previousButton)
        bottomLayout.addWidget(nextButton)
        bottomLayout.addWidget(self.sliderLabel)
        bottomLayout.addWidget(slider)
        bottomLayout.addWidget(fitBordersLabel)
        bottomLayout.addWidget(fitCanvasCheckBox)

        mainLayout.addLayout(bottomLayout)

        self.mainWidget.setLayout(mainLayout)

        self.updateTextFilter()

    def changedFitCanvas(self, state):
        if state == Qt.Checked:
            self.fitCanvasChecked = True
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "true")
        else:
            self.fitCanvasChecked = False
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "false")

    def updateScale(self, value):
        self.currImageScale = value
        self.sliderLabel.setText(f"Image Scale : {self.currImageScale}%")

    def updateCurrPage(self, increment):
        if (self.currPage == 0 and increment == -1) or \
            ((self.currPage + 1) * len(self.imagesButtons) > len(self.foundImages) and increment == 1) or \
            len(self.foundImages) == 0:
            return

        self.currPage += increment
        self.updateImages()

    def updateTextFilter(self):
        newImages = []
        self.currPage = 0

        if self.directoryPath != "":
            it = QDirIterator(self.directoryPath, QDirIterator.Subdirectories)

            while(it.hasNext()):

                stringsInText = self.filterTextEdit.text().lower().split(" ")

                for word in stringsInText:
                    if word in it.filePath().lower() and (".png" in it.filePath() or ".jpg" in it.filePath() or ".jpeg" in it.filePath()):
                        newImages.append(it.filePath())

                it.next()

            if len(self.foundImages) != len(newImages):
                self.foundImages = newImages
                self.updateImages()
            else:
                for i in range(0, len(newImages)):
                    if self.foundImages[i] != newImages[i]:
                        self.foundImages = newImages
                        self.updateImages()
                        return

    def buttonClick(self, position):
        if position < len(self.foundImages) - len(self.imagesButtons) * self.currPage:
            self.addImageLayer(self.foundImages[position + len(self.imagesButtons) * self.currPage])

    def updateImages(self):
        maxWidth = 0
        maxHeight = 0

        buttonsSize = len(self.imagesButtons)

        for i in range(0, buttonsSize):
            if maxWidth < self.imagesButtons[i].width():
                maxWidth = self.imagesButtons[i].width()
            if maxHeight < self.imagesButtons[i].height():
                maxHeight = self.imagesButtons[i].height()

        maxRange = min(len(self.foundImages) - self.currPage * buttonsSize, buttonsSize)

        for i in range(0, len(self.imagesButtons)):
            if i < maxRange:
                icon = QIcon(self.foundImages[i + buttonsSize * self.currPage])

                self.imagesButtons[i].setIcon(icon)
                self.imagesButtons[i].setIconSize(QSize(int(maxWidth), int(maxHeight)))
            else:
                self.imagesButtons[i].setIconSize(QSize(0,0))

    def changePath(self):
        fileDialog = QFileDialog(QWidget(self));
        fileDialog.setFileMode(QFileDialog.DirectoryOnly);

        if self.directoryPath == "":
            self.directoryPath = fileDialog.getExistingDirectory(self.mainWidget, "Change Directory for Images", QStandardPaths.writableLocation(QStandardPaths.PicturesLocation))
            Application.writeSetting(self.applicationName, self.referencesSetting, self.directoryPath)
        else:
            self.directoryPath = fileDialog.getExistingDirectory(self.mainWidget, "Change Directory for Images", self.directoryPath)
            Application.writeSetting(self.applicationName, self.referencesSetting, self.directoryPath)

        self.changePathButton.setText("Change References Directory")
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

    #//
