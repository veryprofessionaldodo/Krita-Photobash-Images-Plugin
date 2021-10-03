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
from .photobash_images_modulo import (
    Photobash_Display,
    Photobash_Button,
)
# //
#\\ Global Variables ###########################################################
# //

class PhotobashDocker(DockWidget):
    application_name = "Photobash"
    references_setting = "referencesDirectory"
    fit_canvas_setting = "fitToCanvas"

    # foundImages = []

    # directoryPath = ""
    # currPage = 0
    curr_image_scale = 100
    fit_canvas_checked = True

    filter_text_edit = None
    main_widget = None
    change_path_button = None
    slider_label = None
    images_buttons = []

    #\\ Initialize #############################################################
    def __init__(self):
        super().__init__()

        # # Source
        # self.Default()

        # Construct
        self.Variables()
        self.User_interface()
        self.Modules()
        #self.Setup()
        #self.Style()
        #self.Settings_Load()

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
        self.directory_plugin = str(
            os.path.dirname(os.path.realpath(__file__)))

        # Photo Bash Docker
        self.window = QWidget()
        self.layout = uic.loadUi(
            self.directory_plugin + '/photobash_images_docker.ui', self.window)
        self.setWidget(self.window)

        # Adjust Layouts
        self.layout.imageWidget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.layout.middleWidget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

    def Modules(self):
        # Display
        self.imageWidget = Photobash_Display(self.layout.imageWidget)
        self.imageWidget.SIGNAL_HOVER.connect(self.cursorHover)
        self.imageWidget.SIGNAL_CLOSE.connect(self.PB_Display_Close)

        self.images_buttons = []

        for i in range(0, self.numImages):
            button = "imagesButtons" + str(i)
            print("vivas!!!", button)
            print(self.layout)
            print(self.layout.imagesButtons0)
            print("ola?")
            print(self.layout["imagesButtons0"])
            print("afinal dá")
            
            image_button = Photobash_Button(self.layout[button])
            image_button.SIGNAL_HOVER.connect(self.cursorHover)
            image_button.SIGNAL_LMB.connect(self.PB_Set_Image)
            image_button.SIGNAL_WUP.connect(self.PB_Wheel_Up)
            image_button.SIGNAL_WDN.connect(self.PB_Wheel_Down)
            image_button.SIGNAL_DISPLAY.connect(self.PB_Display_Open)
            image_button.SIGNAL_BASH.connect(self.PB_Bash)
            image_button.SIGNAL_DRAG.connect(self.PB_Drag)

            self.images_buttons.push(image_button)

    def Setup(self):
        pass

    def Connect(self):
        # UI Top
        # self.layout.filter_text_edit.textChanged.connect(self.Update_Text_Filter)
        self.layout.change_path_button.clicked.connect(self.changePath)
        # UI Bottom
        # self.layout.previousButton.clicked.connect(lambda: self.Update_Current_Page(-1))
        # self.layout.next_button.clicked.connect(lambda: self.Update_Current_Page(1))
        # self.layout.slider.valueChanged.connect(self.Update_Scale)
        # self.layout.fitCanvasCheckBox.stateChanged.connect(self.Changed_Fit_Canvas)

    def Style(self):
        self.cursorHover(None)

    # //
    #\\ Top Functions ##########################################################
    def updateTextFilter(self):
        newImages = []
        self.currPage = 0

        if self.directoryPath != "":
            it = QDirIterator(self.directoryPath, QDirIterator.Subdirectories)

            while(it.hasNext()):

                stringsInText = self.layout.filter_text_edit.text().lower().split(" ")

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

    # //
    #\\ Bottom Functions #######################################################
    def updateCurrPage(self, increment):
        if (self.currPage == 0 and increment == -1) or \
            ((self.currPage + 1) * len(self.images_buttons) > len(self.foundImages) and increment == 1) or \
            len(self.foundImages) == 0:
            return

        self.currPage += increment
        self.updateImages()

    def updateScale(self, value):
        self.curr_image_scale = value
        self.slider_label.setText(f"Image Scale : {self.curr_image_scale}%")  

    def changedFitCanvas(self, state):
        if state == Qt.Checked:
            self.fit_canvas_checked = True
            Application.writeSetting(self.application_name, self.fit_canvas_setting, "true")
        else:
            self.fit_canvas_checked = False
            Application.writeSetting(self.application_name, self.fit_canvas_setting, "false")

    # //
    #\\ Independant Functions ##################################################
    def Clear_Focus(self):
        self.layout.filter_text_edit.clearFocus()

    def cursorHover(self, SIGNAL_HOVER):
        # Reset Hover
        bg_alpha = str("background-color: rgba(0, 0, 0, 50); ")
        # Hover Over
        bg_hover = str("background-color: rgba(0, 0, 0, 100); ")

        # Display Image
        self.layout.imageWidget.setStyleSheet(bg_alpha)
        if SIGNAL_HOVER == "D":
            self.layout.imageWidget.setStyleSheet(bg_hover)
        
        for i in range(0, len(self.images_buttons)):
            button = "imagesButtons" + str(i)

            self.layout[button].setStyleSheet(bg_alpha)
                
            if SIGNAL_HOVER == str(i):
                self.layout[button].setStyleSheet(bg_hover)
        
    def Update_Images(self):
        maxWidth = 0
        maxHeight = 0

        buttonsSize = len(self.images_buttons)

        for i in range(0, buttonsSize):
            if maxWidth < self.images_buttons[i].width():
                maxWidth = self.images_buttons[i].width()
            if maxHeight < self.images_buttons[i].height():
                maxHeight = self.images_buttons[i].height()

        maxRange = min(len(self.foundImages) - self.currPage * buttonsSize, buttonsSize)

        for i in range(0, len(self.images_buttons)):
            if i < maxRange:
                # images_buttons[i].Input_Image(path, QImage(path))

                icon = QIcon(self.foundImages[i + buttonsSize * self.currPage])

                self.images_buttons[i].setIcon(icon)
                self.images_buttons[i].setIconSize(QSize(int(maxWidth), int(maxHeight)))
            else:
                self.images_buttons[i].setIconSize(QSize(0,0))

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

            if self.fit_canvas_checked:
                if activeNode.bounds().width() / activeNode.bounds().height() > doc.bounds().width() / doc.bounds().height():
                    scalingFactor = doc.bounds().width() / activeNode.bounds().width()
                    newWidth = doc.bounds().width() * self.curr_image_scale / 100
                    newHeight = activeNode.bounds().height() * scalingFactor * self.curr_image_scale / 100
                else:
                    scalingFactor = doc.bounds().height() / activeNode.bounds().height()
                    newWidth = activeNode.bounds().width() * scalingFactor * self.curr_image_scale / 100
                    newHeight = doc.bounds().height() * self.curr_image_scale / 100

                    activeNode.scaleNode(QPoint(activeNode.bounds().center().x(),activeNode.bounds().center().y()), int(newWidth), int(newHeight), "Bicubic")
            else:
                newWidth = activeNode.bounds().width() * self.curr_image_scale / 100
                newHeight = activeNode.bounds().height() * self.curr_image_scale / 100

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

    # //
    #\\ Events #################################################################
    def leaveEvent(self, event):
        self.Clear_Focus()
        self.Settings_Save()
    def closeEvent(self, event):
        self.Settings_Save()

    # //
    #\\ Settings ###############################################################
    def Settings_Load(self):
        pass
    def Settings_Save(self):
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
    self.images_buttons0

    sending files to Painter
    path = string with full file path on hardrive
    qimage = QImage(path)
    self.images_buttons0.Input_Image(path, qimage)
    """
    # //



    #\\ Source ###########################################################################################################
    def Default(self):
        # Read settings
        self.directoryPath = Application.readSetting(self.application_name, self.references_setting, "")

        if Application.readSetting(self.application_name, self.fit_canvas_setting, "true") == "true":
            self.fit_canvas_checked = True
        else:
            self.fit_canvas_checked = False

        self.curr_image_scale = 100

        self.setLayout()

    def setLayout(self):
        self.main_widget = QWidget(self)
        self.setWidget(self.main_widget)

        # Filtering text
        self.filter_text_edit = QLineEdit(self.main_widget)
        self.filter_text_edit.setPlaceholderText("Filter images by words...")
        self.filter_text_edit.textChanged.connect(self.updateTextFilter)

        if self.directoryPath != "":
            self.change_path_button = QPushButton("Change References Directory", self.main_widget)
        else:
            self.change_path_button = QPushButton("Set References Directory", self.main_widget)

        self.change_path_button.clicked.connect(self.changePath)

        mainLayout = QVBoxLayout()

        topLayout = QHBoxLayout()
        topLayout.addWidget(self.filter_text_edit)
        topLayout.addWidget(self.change_path_button)

        imagesLayout = QVBoxLayout()

        for i in range(0,3):
            rowLayout = QHBoxLayout()

            for j in range(0,3):
                button = QToolButton(self.main_widget)
                button.setMaximumHeight(3000)
                button.setMaximumWidth(3000)
                button.setMinimumHeight(self.main_widget.height() / 3)
                button.setMinimumWidth(self.main_widget.width() / 3)

                self.images_buttons.append(button)

                rowLayout.addWidget(button)

            imagesLayout.addLayout(rowLayout)

        for i in range(0, len(self.images_buttons)):
            self.images_buttons[i].clicked.connect(lambda: self.buttonClick(i))
        
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(imagesLayout)

        bottomLayout = QHBoxLayout()
        previousButton = QToolButton(self.main_widget)
        previousButton.setMaximumWidth(3000)
        previousButton.clicked.connect(lambda: self.updateCurrPage(-1))
        previousButton.setArrowType(Qt.ArrowType.LeftArrow)

        next_button = QToolButton(self.main_widget)
        next_button.setMaximumWidth(3000)
        next_button.clicked.connect(lambda: self.updateCurrPage(1))
        next_button.setArrowType(Qt.ArrowType.RightArrow)

        self.slider_label = QLabel(self.main_widget)
        self.slider_label.setText(f"Scale : {self.curr_image_scale}%")
        self.slider_label.setMaximumWidth(self.slider_label.fontMetrics().width(self.slider_label.text()))

        slider = QSlider(Qt.Horizontal, self)
        slider.setValue(self.curr_image_scale)
        slider.setMaximum(100)
        slider.setMinimum(10)
        slider.setMaximumWidth(3000)
        slider.valueChanged.connect(self.updateScale)

        fitBordersLabel = QLabel(self.main_widget)
        fitBordersLabel.setText("Fit Canvas")
        fitBordersLabel.setMaximumWidth(fitBordersLabel.fontMetrics().width(fitBordersLabel.text()))

        fitCanvasCheckBox = QCheckBox(self.main_widget)
        fitCanvasCheckBox.setCheckState(self.fit_canvas_checked)
        fitCanvasCheckBox.stateChanged.connect(self.changedFitCanvas)
        fitCanvasCheckBox.setTristate(False)

        bottomLayout.addWidget(previousButton)
        bottomLayout.addWidget(next_button)
        bottomLayout.addWidget(self.slider_label)
        bottomLayout.addWidget(slider)
        bottomLayout.addWidget(fitBordersLabel)
        bottomLayout.addWidget(fitCanvasCheckBox)

        mainLayout.addLayout(bottomLayout)

        self.main_widget.setLayout(mainLayout)

        self.updateTextFilter()

    def buttonClick(self, position):
        if position < len(self.foundImages) - len(self.images_buttons) * self.currPage:
            self.addImageLayer(self.foundImages[position + len(self.images_buttons) * self.currPage])

    def updateImages(self):
        maxWidth = 0
        maxHeight = 0

        buttonsSize = len(self.images_buttons)

        for i in range(0, buttonsSize):
            if maxWidth < self.images_buttons[i].width():
                maxWidth = self.images_buttons[i].width()
            if maxHeight < self.images_buttons[i].height():
                maxHeight = self.images_buttons[i].height()

        maxRange = min(len(self.foundImages) - self.currPage * buttonsSize, buttonsSize)

        for i in range(0, len(self.images_buttons)):
            if i < maxRange:
                icon = QIcon(self.foundImages[i + buttonsSize * self.currPage])

                self.images_buttons[i].setIcon(icon)
                self.images_buttons[i].setIconSize(QSize(int(maxWidth), int(maxHeight)))
            else:
                self.images_buttons[i].setIconSize(QSize(0,0))

    def changePath(self):
        fileDialog = QFileDialog(QWidget(self));
        fileDialog.setFileMode(QFileDialog.DirectoryOnly);

        if self.directoryPath == "":
            self.directoryPath = fileDialog.getExistingDirectory(self.main_widget, "Change Directory for Images", QStandardPaths.writableLocation(QStandardPaths.PicturesLocation))
            Application.writeSetting(self.application_name, self.references_setting, self.directoryPath)
        else:
            self.directoryPath = fileDialog.getExistingDirectory(self.main_widget, "Change Directory for Images", self.directoryPath)
            Application.writeSetting(self.application_name, self.references_setting, self.directoryPath)

        self.change_path_button.setText("Change References Directory")
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

            if self.fit_canvas_checked:
                if activeNode.bounds().width() / activeNode.bounds().height() > doc.bounds().width() / doc.bounds().height():
                    scalingFactor = doc.bounds().width() / activeNode.bounds().width()
                    newWidth = doc.bounds().width() * self.curr_image_scale / 100
                    newHeight = activeNode.bounds().height() * scalingFactor * self.curr_image_scale / 100
                else:
                    scalingFactor = doc.bounds().height() / activeNode.bounds().height()
                    newWidth = activeNode.bounds().width() * scalingFactor * self.curr_image_scale / 100
                    newHeight = doc.bounds().height() * self.curr_image_scale / 100

                    activeNode.scaleNode(QPoint(activeNode.bounds().center().x(),activeNode.bounds().center().y()), int(newWidth), int(newHeight), "Bicubic")
            else:
                newWidth = activeNode.bounds().width() * self.curr_image_scale / 100
                newHeight = activeNode.bounds().height() * self.curr_image_scale / 100

                activeNode.scaleNode(QPoint(activeNode.bounds().center().x(),activeNode.bounds().center().y()), int(newWidth), int(newHeight), "Bicubic")

            # Center image
            offsetX = doc.bounds().width()/2 - activeNode.bounds().center().x()
            offsetY = doc.bounds().height()/2 - activeNode.bounds().center().y()

            activeNode.move(int(offsetX), int(offsetY))

            Krita.instance().activeDocument().refreshProjection()

    # //
