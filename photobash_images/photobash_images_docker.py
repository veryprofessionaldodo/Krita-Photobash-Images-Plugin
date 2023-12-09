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
# along with this 
# program.  If not, see <http://www.gnu.org/licenses/>.

from krita import *
from enum import Enum
from operator import itemgetter
import copy
import math
from PyQt5 import QtWidgets, QtCore, uic
from .photobash_images_modulo import (
    Photobash_Display,
    Photobash_Button,
)
import os.path

class TransparencyType(Enum):
    NONE = 0
    LAYER = 1
    BLEND = 2

class PhotobashDocker(DockWidget):

    def __init__(self):
        super().__init__()

        # Construct
        self.setupVariables()
        self.setupInterface()
        self.setupModules()
        self.setStyle()
        self.initialize()

    def setupVariables(self):
        self.mainWidget = QWidget(self)

        self.applicationName = "Photobash"
        self.referencesSetting = "referencesDirectory"
        self.fitCanvasSetting = "fitToCanvas"
        self.foundFavouritesSetting = "currentFavourites"

        self.currImageScale = 100
        self.fitCanvasChecked = bool(Application.readSetting(self.applicationName, self.fitCanvasSetting, "True"))
        self.imagesButtons = []
        self.foundImages = []
        self.favouriteImages = []
        
        # maps path to image
        self.cachedImages = {}
        self.cachedSearchKeywords = {}
        self.cachedDatePaths = []
        self.order = []
        # store order of push
        self.cachedPathImages = []
        self.maxCachedImages = 90
        self.maxCachedSearchKeyword = 2000
        self.maxNumPages = 9999

        self.currPage = 0
        self.directoryPath = Application.readSetting(self.applicationName, self.referencesSetting, "")
        favouriteImagesValues = Application.readSetting(self.applicationName, self.foundFavouritesSetting, "").split("'")

        for value in favouriteImagesValues:
            if value != "[" and value != ", " and value != "]" and value != "" and value != "[]":
                self.favouriteImages.append(value)

        self.bg_alpha = str("background-color: rgba(0, 0, 0, 50); ")
        self.bg_hover = str("background-color: rgba(0, 0, 0, 100); ")

    def setupInterface(self):
        # Window
        self.setWindowTitle("Photobash Images")

        # Path Name
        self.directoryPlugin = str(os.path.dirname(os.path.realpath(__file__)))

        # Photo Bash Docker
        self.mainWidget = QWidget(self)
        self.setWidget(self.mainWidget)

        self.layout = uic.loadUi(self.directoryPlugin + '/photobash_images_docker.ui', self.mainWidget)

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
        self.layout.imageWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.layout.middleWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # setup connections for top elements
        self.layout.filterTextEdit.textChanged.connect(self.textFilterChanged)
        self.layout.changePathButton.clicked.connect(self.changePath)
        # setup connections for bottom elements
        self.layout.previousButton.clicked.connect(lambda: self.updateCurrentPage(-1))
        self.layout.nextButton.clicked.connect(lambda: self.updateCurrentPage(1))
        self.layout.refresh.clicked.connect(self.refresh_cache)
        self.layout.dateSort.stateChanged.connect(self.sortByDate)
        self.layout.scaleSlider.valueChanged.connect(self.updateScale)
        self.layout.paginationSlider.setMinimum(0)
        self.layout.paginationSlider.valueChanged.connect(self.updatePage)
        self.layout.fitCanvasCheckBox.stateChanged.connect(self.changedFitCanvas)
        self.sortImagesByDate = False

    def refresh_cache(self):
        self.favouriteImages = []
        self.foundImages = []
        self.cachedSearchKeywords = {}
        self.getImagesFromDirectory()

    def sortByDate(self,state):
        if state == Qt.Checked:
            self.sortImagesByDate = True
            self.order = copy.deepcopy(self.foundImages)
        else:
            self.sortImagesByDate = False
            self.foundImages = copy.deepcopy(self.order)
        self.reorganizeImages()
        self.updateImages()


    def setupModules(self):
        # Display Single
        self.imageWidget = Photobash_Display(self.layout.imageWidget)
        self.imageWidget.SIGNAL_HOVER.connect(self.cursorHover)
        self.imageWidget.SIGNAL_CLOSE.connect(self.closePreview)

        # Display Grid
        self.imagesButtons = []
        for i in range(0, len(self.layoutButtons)):
            layoutButton = self.layoutButtons[i]
            imageButton = Photobash_Button(layoutButton)
            imageButton.setNumber(i)
            imageButton.SIGNAL_HOVER.connect(self.cursorHover)
            imageButton.SIGNAL_LMB.connect(self.buttonClick)
            imageButton.SIGNAL_WUP.connect(lambda: self.updateCurrentPage(-1))
            imageButton.SIGNAL_WDN.connect(lambda: self.updateCurrentPage(1))
            imageButton.SIGNAL_PREVIEW.connect(self.openPreview)
            imageButton.SIGNAL_FAVOURITE.connect(self.pinToFavourites)
            imageButton.SIGNAL_UN_FAVOURITE.connect(self.unpinFromFavourites)
            imageButton.SIGNAL_OPEN_NEW.connect(self.openNewDocument)
            imageButton.SIGNAL_REFERENCE.connect(self.placeReference)
            imageButton.SIGNAL_ADD_WITH_TRANS_LAYER.connect(self.add_with_layer)
            imageButton.SIGNAL_ADD_WITH_ERASE_GROUP.connect(self.add_with_blend)
            imageButton.SIGNAL_MMD.connect(self.add_image_with_layer)
            imageButton.SIGNAL_CTRL_LEFT.connect(self.add_image_with_group)
            self.imagesButtons.append(imageButton)

    def setStyle(self):
        # Displays
        self.cursorHover(None)

    def initialize(self):
        # initialize based on what was setup
        if self.directoryPath != "":
            self.layout.changePathButton.setText("Change References Folder")
            self.getImagesFromDirectory()
            self.layout.fitCanvasCheckBox.setChecked(self.fitCanvasChecked)

        # initial organization of images with favourites
        self.reorganizeImages()
        self.layout.scaleSliderLabel.setText(f"Image Scale : 100%")

        self.updateImages()
        self.getImagesFromDirectory()

    def reorganizeImages(self):
        # organize images, taking into account favourites
        # and their respective order
        favouriteFoundImages = []
        for image in self.favouriteImages:
            if image in self.foundImages:
                self.foundImages.remove(image)
                favouriteFoundImages.append(image)
        if not self.sortImagesByDate:
            self.foundImages = favouriteFoundImages + self.foundImages
        else:
            cachedDates = self.cachedDatePaths[:]
            for i in self.cachedDatePaths:
                if i['value'] not in self.foundImages:
                    cachedDates.remove(i)
            favouriteDateImages = []
            for favourite in self.favouriteImages:
                for image in self.cachedDatePaths:
                    if image['value'] == favourite:
                        cachedDates.remove(image)
                        favouriteDateImages.append(image)
                        break
            sorted_dates = sorted(favouriteDateImages,key=itemgetter('date'),reverse=True) + sorted(cachedDates,key=itemgetter('date'),reverse=True)
            self.foundImages = [image['value'] for image in sorted_dates]

    def textFilterChanged(self):
        stringsInText = self.layout.filterTextEdit.text().lower().split(" ")
        if self.layout.filterTextEdit.text().lower() == "":
            self.foundImages = copy.deepcopy(self.allImages)
            self.reorganizeImages()
            self.updateImages()
            return 

        newImages = []
        for word in stringsInText:
            for path in self.allImages:
                # exclude path outside from search
                if word in path.replace(self.directoryPath, "").lower() and not path in newImages and word != "" and word != " ":
                    newImages.append(path)
                elif path in self.cachedSearchKeywords:
                    searchString = ",".join(self.cachedSearchKeywords[path]).lower()
                    if word in searchString and not path in newImages and word != "" and word != " ":
                        newImages.append(path)

        self.foundImages = newImages
        self.order = copy.deepcopy(self.foundImages)
        self.reorganizeImages()
        self.updateImages()

    def getImagesFromDirectory(self):
        newImages = []
        self.currPage = 0

        if self.directoryPath == "":
            self.foundImages = []
            self.favouriteImages = []
            self.updateImages()
            return 

        it = QDirIterator(self.directoryPath, QDirIterator.Subdirectories)

        cache_date_paths = []
        while(it.hasNext()):
            if (".webp" in it.filePath() or ".png" in it.filePath() or ".jpg" in it.filePath() or ".jpeg" in it.filePath()) and \
                (not ".webp~" in it.filePath() and not ".png~" in it.filePath() and not ".jpg~" in it.filePath() and not ".jpeg~" in it.filePath()):
                self.cacheSearchTerms(it.filePath())
                newImages.append(it.filePath())
                cache_date_paths.append({
                    'date':os.path.getmtime(it.filePath()),
                    'value':it.filePath()
                })
            it.next()
        self.cachedDatePaths = sorted(cache_date_paths,key=itemgetter('date'),reverse=True)
        self.foundImages = copy.deepcopy(newImages)
        self.allImages = copy.deepcopy(newImages)
        self.reorganizeImages()
        self.updateImages()

    def cacheSearchTerms(self,key):
        baseName = os.path.basename(key)
        fileName = os.path.splitext(baseName)[0]
        keywordFile = self.directoryPath +"/"+ fileName +'.txt'
        if os.path.exists(keywordFile):
            with open(keywordFile,'r') as searchFile:
                lines = searchFile.readlines(self.maxCachedSearchKeyword)
                self.cachedSearchKeywords[key] = lines
                
    def updateCurrentPage(self, increment):
        if (self.currPage == 0 and increment == -1) or \
            ((self.currPage + 1) * len(self.imagesButtons) > len(self.foundImages) and increment == 1) or \
            len(self.foundImages) == 0:
            return

        self.currPage += increment
        maxNumPage = math.ceil(len(self.foundImages) / len(self.layoutButtons))
        self.currPage = max(0, min(self.currPage, maxNumPage - 1))
        self.updateImages()

    def updateScale(self, value):
        self.currImageScale = value
        self.layout.scaleSliderLabel.setText(f"Image Scale : {self.currImageScale}%")

        # update layout buttons, needed when dragging
        self.imageWidget.setImageScale(self.currImageScale)

        # normal images
        for i in range(0, len(self.imagesButtons)):
            self.imagesButtons[i].setImageScale(self.currImageScale)

    def updatePage(self, value):
        maxNumPage = math.ceil(len(self.foundImages) / len(self.layoutButtons))
        self.currPage = max(0, min(value, maxNumPage - 1))
        self.updateImages()

    def changedFitCanvas(self, state):
        if state == Qt.Checked:
            self.fitCanvasChecked = True
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "true")
        else:
            self.fitCanvasChecked = False
            Application.writeSetting(self.applicationName, self.fitCanvasSetting, "false")

        # update layout buttons, needed when dragging
        self.imageWidget.setFitCanvas(self.fitCanvasChecked)

        # normal images
        for i in range(0, len(self.imagesButtons)):
            self.imagesButtons[i].setFitCanvas(self.fitCanvasChecked)

    def cursorHover(self, SIGNAL_HOVER):
        # Display Image
        self.layout.imageWidget.setStyleSheet(self.bg_alpha)
        if SIGNAL_HOVER == "D":
            self.layout.imageWidget.setStyleSheet(self.bg_hover)

        # normal images
        for i in range(0, len(self.layoutButtons)):
            self.layoutButtons[i].setStyleSheet(self.bg_alpha)

            if SIGNAL_HOVER == str(i):
                self.layoutButtons[i].setStyleSheet(self.bg_hover)

    # checks if image is cached, and if it isn't, create it and cache it
    def getImage(self, path):
        if path in self.cachedPathImages:
            return self.cachedImages[path]

        # need to remove from cache
        if len(self.cachedImages) > self.maxCachedImages: 
            removedPath = self.cachedPathImages.pop()
            self.cachedImages.pop(removedPath)
            if removedPath in self.cachedSearchKeywords:
                self.cachedSearchKeywords.pop(removedPath)
            for i in self.cachedDatePaths[:]:
                if i['value'] == removedPath:
                    self.cachedDatePaths.remove(i)
                    break
        self.cachedPathImages = [path] + self.cachedPathImages
        self.cachedImages[path] = QImage(path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return self.cachedImages[path]
    
    def splitPathName(self,path):
        baseName = os.path.basename(path)
        return baseName
    # makes sure the first 9 found images exist
    def checkValidImages(self):
        found = 0
        for path in self.foundImages:
            if found == 9:
                return

            if self.checkPath(path):
                found = found + 1

    def updateImages(self):
        self.checkValidImages()
        buttonsSize = len(self.imagesButtons)

        # don't try to access image that isn't there
        maxRange = min(len(self.foundImages) - self.currPage * buttonsSize, buttonsSize)

        for i in range(0, len(self.imagesButtons)):
            if i < maxRange:
                # image is within valid range, apply it
                path = self.foundImages[i + buttonsSize * self.currPage]
                self.imagesButtons[i].setFavourite(path in self.favouriteImages)
                self.imagesButtons[i].setImage(path, self.getImage(path))
            else:
                # image is outside the range
                self.imagesButtons[i].setFavourite(False)
                self.imagesButtons[i].setImage("",None)

        # update text for pagination
        maxNumPage = math.ceil(len(self.foundImages) / len(self.layoutButtons))
        currPage = self.currPage + 1

        if maxNumPage == 0:
            currPage = 0

        # normalize string length
        if currPage < 10:
            currPage = "   " + str(currPage)
        elif currPage < 100:
            currPage = "  " + str(currPage)
        elif currPage < 1000:
            currPage = " " + str(currPage)

        # currPage is the index, but we want to present it in a user friendly way,
        # so it starts at 1
        self.layout.paginationLabel.setText(f"Page: {currPage}/{str(maxNumPage)}")
        # correction since array begins at 0
        self.layout.paginationSlider.setRange(0, maxNumPage - 1)
        self.layout.paginationSlider.setSliderPosition(self.currPage)


    def add_image_with_layer(self,position):
        if position < len(self.foundImages) - len(self.imagesButtons) * self.currPage:
            self.addImageLayer(self.foundImages[position + len(self.imagesButtons) * self.currPage],TransparencyType.LAYER)

    def add_image_with_group(self,position):
        if position < len(self.foundImages) - len(self.imagesButtons) * self.currPage:
            self.addImageLayer(self.foundImages[position + len(self.imagesButtons) * self.currPage],TransparencyType.BLEND)
    def add_with_layer(self,photoPath):
        self.addImageLayer(photoPath,TransparencyType.LAYER)

    def add_with_blend(self,photoPath):
        self.addImageLayer(photoPath,TransparencyType.BLEND)

    def addImageLayer(self, photoPath,transparency_type):
        # file no longer exists, remove from all structures
        if not self.checkPath(photoPath):
            self.updateImages()
            return
        
        # Get the document:
        doc = Krita.instance().activeDocument()

        # Saving a non-existent document causes crashes, so lets check for that first.
        if doc is None:
            return 

        # Check if there is a valid Canvas to place the Image
        if self.canvas() is None or self.canvas().view() is None:
            return 

        scale = self.currImageScale / 100

        # Scale Image
        if self.fitCanvasChecked:
            image = QImage(photoPath).scaled(int(doc.width() * scale), int(doc.height() * scale), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            image = QImage(photoPath)
            # scale image
            image = image.scaled(int(image.width() * scale), int(image.height() * scale), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # MimeData
        mimedata = QMimeData()
        url = QUrl().fromLocalFile(photoPath)
        mimedata.setUrls([url])
        mimedata.setImageData(image)

        # get doc data
        root = doc.rootNode()
        active_node = doc.activeNode()

        # get base name
        file_name = os.path.basename(photoPath)

        # create layer with base name
        new_layer = doc.createNode(file_name,'paintlayer')

        # copy bytes from qImage into the image layer
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        new_layer.setPixelData(QByteArray(ptr.asstring()),0,0,image.width(),image.height())

        # center the layer
        center_x = int((doc.width() - image.width())/2)
        center_y = int((doc.height() - image.height())/2)
        new_layer.move(center_x,center_y)
        if transparency_type == TransparencyType.NONE or transparency_type == TransparencyType.LAYER:
            root.addChildNode(new_layer,None)
        if transparency_type == TransparencyType.LAYER:
            ## create a layer
            transparency_layer = doc.createTransparencyMask('transparencymask')
            
            ## fill with white
            trans_image = image.scaled(doc.width(),doc.height(), Qt.IgnoreAspectRatio, Qt.FastTransformation)
            trans_image.fill(QColor('white'))

            ## copy bytes over
            trans_pointer = trans_image.bits()
            trans_pointer.setsize(trans_image.byteCount())
            transparency_layer.setPixelData(QByteArray(trans_pointer.asstring()),0,0,doc.width(),doc.height())

            new_layer.addChildNode(transparency_layer,None)

            ## move layer so centered image is not cropped.
            transparency_layer.move(0,0)
            
        if transparency_type == transparency_type.BLEND:
            new_group = doc.createGroupLayer(file_name)
            root.addChildNode(new_group,None)
            erase = doc.createNode('erase','paintLayer')
            erase.setBlendingMode('erase')
            new_group.addChildNode(new_layer,None)
            new_group.addChildNode(erase,None)


       #Refresh Canvas
        Krita.instance().activeDocument().refreshProjection()

    def checkPath(self, path):
        if not os.path.isfile(path):
            if path in self.foundImages:
                self.foundImages.remove(path)
            if path in self.allImages:
                self.allImages.remove(path)
            if path in self.favouriteImages:
                self.favouriteImages.remove(path)
            if path in self.cachedSearchKeywords:
                self.cachedSearchKeywords.remove(path)
            for i in self.cachedDatePaths[:]:
                if i['value'] == path:
                    self.cachedDatePaths.remove(i)
                    break
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Missing Image!")
            dlg.setText("This image you tried to open was not found. Removing from the list.")
            dlg.exec()

            return False

        return True

    def openNewDocument(self, path):
        if not self.checkPath(path):
            self.updateImages()
            return 

        document = Krita.instance().openDocument(path)
        Application.activeWindow().addView(document)

    def placeReference(self, path):
        if not self.checkPath(path):
            self.updateImages()
            return

        # MimeData
        mimedata = QMimeData()
        url = QUrl().fromLocalFile(path)
        mimedata.setUrls([url])
        image = QImage(path)
        mimedata.setImageData(image)

        QApplication.clipboard().setImage(image)
        Krita.instance().action('paste_as_reference').trigger()

    def openPreview(self, path):
        image = QImage(path)
        self.imageWidget.setImage(path,image)
        self.layout.imageWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.middleWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)

    def closePreview(self):
        self.layout.imageWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        self.layout.middleWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def pinToFavourites(self, path):
        self.currPage = 0
        self.favouriteImages = [path] + self.favouriteImages

        # save setting for next restart
        Application.writeSetting(self.applicationName, self.foundFavouritesSetting, str(self.favouriteImages))
        self.reorganizeImages()
        self.updateImages()

    def unpinFromFavourites(self, path):
        if path in self.favouriteImages:
            self.favouriteImages.remove(path)

        Application.writeSetting(self.applicationName, self.foundFavouritesSetting, str(self.favouriteImages))

        # resets order to the default, but checks if foundImages is only a subset
        # in case it is searching
        orderedImages = []
        for image in self.allImages:
            if image in self.foundImages:
                orderedImages.append(image)

        self.foundImages = orderedImages
        self.reorganizeImages()
        self.updateImages()

    def leaveEvent(self, event):
        self.layout.filterTextEdit.clearFocus()

    def canvasChanged(self, canvas):
        pass

    def buttonClick(self, position):
        if position < len(self.foundImages) - len(self.imagesButtons) * self.currPage:
            self.addImageLayer(self.foundImages[position + len(self.imagesButtons) * self.currPage],TransparencyType.NONE)

    def changePath(self):
        fileDialog = QFileDialog(QWidget(self))
        fileDialog.setFileMode(QFileDialog.DirectoryOnly)

        if self.directoryPath == "":
            path = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        else:
            path = QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        
        title = "Change Directory for Images"
        dialogOptions = QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog
        new_path = fileDialog.getExistingDirectory(self.mainWidget, title, path, dialogOptions)
        if self.directoryPath != "" and new_path == "":
            return
        self.directoryPath = new_path
        Application.writeSetting(self.applicationName, self.referencesSetting, self.directoryPath)

        self.favouriteImages = []
        self.foundImages = []
        self.cachedSearchKeywords = {}
        self.cachedDatePaths = []
        Application.writeSetting(self.applicationName, self.foundFavouritesSetting, "")

        if self.directoryPath == "":
            self.layout.changePathButton.setText("Set References Folder")
        else:
            self.layout.changePathButton.setText("Change References Folder")

        self.getImagesFromDirectory()
