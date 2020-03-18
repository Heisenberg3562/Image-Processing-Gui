import cv2
import os 
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy,QInputDialog)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

class ImageViewer(QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0
        self.directory=""

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)

        self.createActions()
        self.createMenus()
        
        self.setWindowTitle("IOA Image Viewer")
        self.resize(800, 600)

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                QDir.currentPath())
        self.directory=fileName
        print(fileName)
        if fileName:
            image = QImage(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()
        self.updateActions()

    def faceDetect(self):
        try:
            face_cascade = cv2.CascadeClassifier(r"FaceRcognition-master\haarcascade_frontalface_default.xml")
            img = cv2.imread(self.directory)
            grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            faces = face_cascade.detectMultiScale(grey_img,
            scaleFactor=1.05,
            minNeighbors=5)
            c=0
            #crop=[]
            #print(type(faces))
            #print(faces)
            for x, y, w, h in faces:
                #crop.append(img[y:y+h,x:x+w])
                #crimg=cv2.circle(img, (x+int(h/2), y+int(w/2)), int(h/2), (0, 255, 0), 3)
                img = cv2.rectangle(img, (x,y), (x+w, y+w), (0,255,0), 2)
                c=c+1
            #a=0
            #print(c)
            # for cimg in crop:
            #     name="face detected image"+str(c)
            #     cv2.imshow(name, cimg)
            #     c+=1
            #self.imageLabel.setPixmap(img)
            #print(QDir.currentPath)
            cv2.imwrite("Detected.jpg",img)
            #print(os.getcwd())
            cdr=str(os.getcwd())+'\Detected.jpg'
            #pic = cdr[:-2]+"Detected.jpg'"
            image = QImage(cdr)
            if image.isNull():
                QMessageBox.information(self, "IOA Image Viewer",
                        "Cannot load %s." % cdr)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(image))
            # cv2.imshow("face detected image", img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        except:
            pass
    
    def imgResize(self):
        try:
            img = cv2.imread(self.directory,1)
            oheight, owidth = img.shape[0:2]
            iheight, hokPressed = QInputDialog.getInt(self, "Get Height","Height :", 0, 0, int(oheight), 1)
            iwidth , okPressed = QInputDialog.getInt(self, "Get Width","Width :", 0, 0, int(owidth), 1)
            resizedImg = cv2.resize(img,(int(iwidth),int(iheight)))
            print(iheight)
            print(iwidth)
            cv2.imwrite("Resized.jpg",resizedImg)
            cdr=str(os.getcwd())+'\\Resized.jpg'
            Rimage = QImage(cdr)
            if Rimage.isNull():
                QMessageBox.information(self, "IOA Image Viewer",
                        "Cannot load %s." % cdr)
                return
            self.imageLabel = QLabel()
            self.imageLabel.setPixmap(QPixmap.fromImage(Rimage))
            self.scaleFactor = 1.0
        except:
            pass


            # scale_percent = 100 # percent of original size
            # width = int(img.shape[1] * scale_percent / 100)
            # height = int(img.shape[0] * scale_percent / 100)
            # dim = (width, height)
            # resized = cv2.resize(img, dim)

    
    def imgRotate(self):
        try:
            img = cv2.imread(self.directory)
            height, width = img.shape[0:2]
            rotationMatrix = cv2.getRotationMatrix2D((width/2, height/2), 90, .5)
            rotatedImage = cv2.warpAffine(img, rotationMatrix, (width, height))
            cv2.imwrite("Rotated.jpg",rotatedImage)
            cdr=str(os.getcwd())+'\\Rotated.jpg'
            rimage = QImage(cdr)
            if rimage.isNull():
                QMessageBox.information(self, "IOA Image Viewer",
                        "Cannot load %s." % cdr)
                return

            self.imageLabel.setPixmap(QPixmap.fromImage(rimage))
            self.scaleFactor = 1.0
        except:
            pass

    def imgCrop(self):
        try:
            img = cv2.imread(self.directory)
            face_cascade = cv2.CascadeClassifier(r"FaceRcognition-master\haarcascade_frontalface_default.xml")
            for x,y,w,h in faces:
                img = cv2.rectangle(img,(x,y),(x+w, y+w),(0,255,0),1)
                cropped = img[y:y+h, x:x+w]
            cv2.imwrite("Rotated.jpg",cropped)
            cdr=str(os.getcwd())+'\\Rotated.jpg'
            image = QImage(cdr)
            if image.isNull():
                QMessageBox.information(self, "IOA Image Viewer",
                        "Cannot load %s." % cdr)
                return
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
        except:
            pass


    # def imgBlur(self):
    #     img = cv2.imread(self.directory)
    #     blur_image = cv2.GaussianBlur(img, (7,7), 0) 
        #scale 1,2,3,4,5



    # def imgEdge(self):
    #     edge_img = cv2.Canny(img,100,200)



    #def imgDenoise(self):
        # result = cv2.fastNlMeansDenoisingColored(img,None,20,10,7,21)

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++",
                enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-",
                enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S",
                enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
                checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.faceDetectAct = QAction("Face Detect",self,triggered=self.faceDetect,enabled=False)

        self.resizeAct = QAction("Resize",self,triggered=self.imgResize,enabled=False)

        self.rotateAct = QAction("Rotate", self,triggered=self.imgRotate, enabled=False)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.optionsMenu = QMenu("&Options", self)
        self.optionsMenu.addAction(self.faceDetectAct)
        self.optionsMenu.addAction(self.resizeAct)
        self.optionsMenu.addAction(self.rotateAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.optionsMenu)
        self.menuBar().addMenu(self.helpMenu)
        

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.resizeAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.faceDetectAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.rotateAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.show()
    sys.exit(app.exec_())

 
# Resize:
# Height ,width

# Rotate:
# Angle

# Crop:
# start (x,y) yeh start end
# end (x,y)

# Blur:
# 1,2,3,4,5 scale

# Edges:

# Denoise:   

# Background remove: