# This Python file uses the following encoding: utf-8
import sys
import os
import os.path
import io
import pickle
import ebooklib
from ebooklib import epub
import PIL
from PIL.ImageQt import ImageQt
from PyPDF2 import PdfFileReader
from pdf2image import convert_from_path
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import resources_rc
from Library import *
from GuiHelper import *
#import logging

#logging.basicConfig(filename='D:/MyLog.log',level=logging.DEBUG)


qt_creator_file = "mainwindow.ui"
qt_dialog_file = "renamedialog.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)


     
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.verticalLayout.addWidget(self.tabWidget)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Witaj", 2000)
        
        self.index = 0
        self.modelsList = []
        self.tabViewList = []
        self.addTab("Nowa lista")
        
        
        self.actionDelete.triggered.connect(self.deleteBook)
        self.actionNewList.triggered.connect(self.addTab)
        self.actionDeleteList.triggered.connect(self.deleteCurrentTab)
        self.actionMarkCompleted.triggered.connect(self.markAsCompleted)
        self.actionFavourite.triggered.connect(self.markAsFavourite)
        self.actionAdd.triggered.connect(self.addToList)
        self.actionRenameList.triggered.connect(self.renameTab)
        self.actionSaveList.triggered.connect(self.saveList)
        self.actionOpenList.triggered.connect(self.readList)
        self.actionSortAuthorAlpha.triggered.connect(self.sortAuthorAlpha)
        self.actionSortAuthorRev.triggered.connect(self.sortAuthorRev)
        self.actionSortTitleAlpha.triggered.connect(self.sortTitleAlpha)
        self.actionSortTitleRev.triggered.connect(self.sortTitleRev)
        self.actionSortFav.triggered.connect(self.sortFav)
        self.actionSortComp.triggered.connect(self.sortComp)
        self.actionOpen.triggered.connect(self.openFile)
        
        self.tabWidget.currentChanged.connect(self.onTabChange)
        self.tabWidget.tabBarDoubleClicked.connect(self.deleteTab)
    
    def confirm(self):
        box = QtWidgets.QMessageBox()
        box.setIcon(QtWidgets.QMessageBox.Question)
        box.setWindowTitle('Potwierdzenie')
        box.setText('Czy na pewno?')
        box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
        yesButton = box.button(QtWidgets.QMessageBox.Yes)
        yesButton.setText('Tak')
        noButton = box.button(QtWidgets.QMessageBox.No)
        noButton.setText('Nie')
        box.exec_()

        if box.clickedButton() == yesButton:
            return True
        elif box.clickedButton() == noButton:
            return False
        
    def closeEvent(self, event):
        reply = self.confirm()

        if reply == True:
            event.accept()
        else:
            event.ignore()
    
    def addBook(self, title, author, cover=None, filepath=None, isfav = False, iscomp = False):
        
        bookW = BookWidget()
        if title is not None and title.strip() != '':
            bookW.setTitle(title)
        else:
            notitle = filepath.split(r"/")
            notitle = notitle[len(notitle)-1]
            bookW.setTitle(notitle)
            title = notitle
        if author is not None and author.strip() != '':
            bookW.setAuthor(author)
        else:
            author = "Autor nieznany"
            bookW.setAuthor("Autor nieznany")
        if cover is None or not isinstance(cover, bytes):
            bookW.setIconFromPath(":/images/nocover.png")
        else:
            bookW.setIconFromBytes(cover)   
        book = Book(title, author, filepath)
        if isfav:
            book.toggleFavourite()
            bookW.toggleFav()
        if iscomp:
            book.toggleCompleted()
            bookW.toggleCom()
        self.modelsList[self.index].books.append(book)
        myQListWidgetItem = QtWidgets.QListWidgetItem(self.tabViewList[self.index])
        myQListWidgetItem.setSizeHint(bookW.sizeHint())
        self.tabViewList[self.index].addItem(myQListWidgetItem)
        self.tabViewList[self.index].setItemWidget(myQListWidgetItem, bookW)                
    
    def getFiles(self, path=r"C:\Users\Marcin\Desktop\test", filetype="Pliki dokumentów (*.epub *.pdf)"):
        fname = QtWidgets.QFileDialog.getOpenFileNames(self, 'Wybierz plik', path, filetype)
        return fname[0]
        
    def getFile(self, path=r"C:\Users\Marcin\Desktop\test", filetype="Pliki dokumentów (*.epub *.pdf)"):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Wybierz plik', path, filetype)
        return fname
        
    def getFolder(self, path=r"C:\Users\Marcin\Desktop\test\Listy"):
        fname =  QtWidgets.QFileDialog.getExistingDirectory(self, 'Open working directory', path)
        return fname
        
    def addToList(self):
        self.statusbar.showMessage("Trwa dodawanie", 200000)
        self.prepareToAdd(self.getFiles())
        self.statusbar.showMessage("Dodano pomyślnie", 2000)
        
    def extractInfo(self, path):
        with open(path, 'rb') as f:
            pdf = PdfFileReader(f)
            info = pdf.getDocumentInfo()
        image = convert_from_path(path, last_page=1)
        imageout = image[0]
        bytesstream = io.BytesIO()
        imageout.save(bytesstream, 'JPEG')
        imageout.__class__ = PIL.Image.Image

        return (info.title, info.author, bytesstream.getvalue())
         
    def prepareToAdd(self, filenamelist, flag = 0):
        for file in filenamelist:
            if file.endswith(".epub"):
                try:
                    book = epub.read_epub(file)
                except Exception as e:
                    self.error("Błąd pliku: " + str(e))
                title = book.get_metadata("DC","title")[0][0]
                author = book.get_metadata("DC","creator")[0][0]
                try:
                    cover = book.get_item_with_id('cover-image').get_content()
                except:
                    cover = None
                if cover is None:
                    try:
                        cover = next(book.get_items_of_type(ebooklib.ITEM_IMAGE)).get_content()
                    except:
                        cover = None
                if flag == 1:
                    self.addBook(title, author, cover, file, isfav = True)
                elif flag == 2:
                    self.addBook(title, author, cover, file, iscomp = True)
                else:
                    self.addBook(title, author, cover, file)
            elif file.endswith(".pdf"):               
                info = None
                try:
                    info = self.extractInfo(file)    
                except Exception as e:
                    self.error("Błąd pliku: " + str(e))
                title = info[0]
                author = info[1]
                cover = info[2]
                if flag == 1:
                    self.addBook(title, author, cover, file, isfav = True)
                elif flag == 2:
                    self.addBook(title, author, cover, file, iscomp = True)
                else:
                    self.addBook(title, author, cover, file)
            else:
                return
        
    def addTab(self, tabname = False):
        dialog = RenameDialog(self)
        if tabname is False:   
            dialog.exec()
            if dialog.inputValue().strip() != '':
                tabname = dialog.inputValue()
            if dialog.change is False:
                return
        if tabname is False:
            tabname = "Nowa lista"
        newtab = QtWidgets.QWidget()
        verticalLayout = QtWidgets.QVBoxLayout(newtab)
        newlist = QtWidgets.QListWidget(newtab)
        newlist.doubleClicked.connect(self.openFile)
        self.tabViewList.append(newlist)
        index = self.tabWidget.count()
        self.index = index
        verticalLayout.addWidget(self.tabViewList[self.index])
        self.tabWidget.addTab(newtab, tabname)
        self.tabWidget.setCurrentIndex(index)
        self.modelsList.append(TabModel())
        
        return self.tabWidget.count()

    def deleteBook(self):
        listItems=self.tabViewList[self.index].selectedItems()
        if not listItems: return
        for item in listItems:
            del self.modelsList[self.index].books[self.tabViewList[self.index].row(item)]
            self.tabViewList[self.index].takeItem(self.tabViewList[self.index].row(item))
    
    def deleteCurrentTab(self):
        self.deleteTab(self.index)
    
    def deleteTab(self, index):
        if not self.confirm(): return
        if not self.tabWidget.count(): return
        del self.modelsList[index]
        del self.tabViewList[index]
        self.tabWidget.removeTab(index)
        
    def renameTab(self):
        dialog = RenameDialog(self)
        dialog.exec()
        if dialog.change == False:
            return
        if dialog.inputValue().strip() != '':
            self.tabWidget.setTabText(self.index, dialog.inputValue())
        
    def markAsCompleted(self):
        listItems=self.tabViewList[self.index].selectedItems()
        if not listItems: return
        for item in listItems:
            self.modelsList[self.index].books[self.tabViewList[self.index].row(item)].toggleCompleted()
            self.tabViewList[self.index].itemWidget(item).toggleCom()
            
    def markAsFavourite(self):
        listItems=self.tabViewList[self.index].selectedItems()
        if not listItems: return
        for item in listItems:
            self.modelsList[self.index].books[self.tabViewList[self.index].row(item)].toggleFavourite()
            self.tabViewList[self.index].itemWidget(item).toggleFav()
            
    def onTabChange(self):
        self.index = self.tabWidget.currentIndex()
        
    def error(self, txt):
        print(txt)

    def saveList(self):
        folder = self.getFolder()
        filename = folder + "/"+ self.tabWidget.tabText(self.index) + ".list"
        if folder != '':
            with open(filename, 'wb') as f:
                data = pickle.dump(self.modelsList[self.index].books, f)
                self.statusbar.showMessage("Zapisano pomyślnie", 2000)
            return
        self.statusbar.showMessage("Anulowano", 2000)
           
    def readList(self): 
        self.statusbar.showMessage("Trwa dodawanie", 200000)
        try:
            filename = self.getFile(filetype="Pliki list (*.list)")[0]
        except:
            return
        listname = filename.split("/")
        listname = listname[len(listname)-1]
        listname = listname.split('.')[0]
        skipcounter = 0
        data = None
        
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f) 
        except:
            self.statusbar.showMessage("Błąd pliku", 2000)
            return
        if data is None or data == []:
            self.statusbar.showMessage("Plik zawiera pustą listę", 2000)
            return
        self.addTab(listname)

        filenamelist = []
        for book in data:
            if os.path.isfile(book.filepath):
                filenamelist.append(book.filepath)
            else:
                skipcounter += 1
        if skipcounter > 0:
            self.statusbar.showMessage("Pominięto " + str(skipcounter) + " plików, których nie znaleziono", 2000)
        if len(filenamelist) > 0 and skipcounter == 0:
            self.prepareToAdd(filenamelist)
            self.statusbar.showMessage("Wczytano pomyślnie", 2000)
        elif len(filenamelist) > 0:
            self.prepareToAdd(filenamelist)
        elif skipcounter == 0:
            self.statusbar.showMessage("Plik zawiera pustą listę", 2000)
         
    def mySort(self, key, reverse = False):
        books = self.modelsList[self.index].books.copy()
        books.sort(reverse = reverse,key = key)
        self.statusbar.showMessage("Trwa dodawanie", 200000)
        self.addTab()
        filenames = []
        for book in books:
            filenames.append(book.filepath)
        self.prepareToAdd(filenames)
        self.statusbar.showMessage("Dodano pomyślnie", 2000)

    def myFilter(self, myfilter, flag = 0):
        books = self.modelsList[self.index].books.copy()
        books = filter(myfilter, books)
        self.statusbar.showMessage("Trwa dodawanie", 200000)
        self.addTab()
        filenames = []
        for book in books:
            filenames.append(book.filepath)
        self.prepareToAdd(filenames, flag)
        self.statusbar.showMessage("Dodano pomyślnie", 2000)
   
    def sortAuthorAlpha(self):
        self.mySort(lambda x: x.author)
            
    def sortAuthorRev(self):
        self.mySort(lambda x: x.author, True)
        
    def sortTitleAlpha(self):
        self.mySort(lambda x: x.title)

    def sortTitleRev(self):
        self.mySort(lambda x: x.title, True)
    
    def sortFav(self):
        self.myFilter(lambda x: True if x.favourite else False, 1)
    
    def sortComp(self):
        self.myFilter(lambda x: True if x.completed else False, 2)
    
    def openFile(self):
        listItems=self.tabViewList[self.index].selectedItems()
        if not listItems: return
        try:
            for item in listItems:
                filepath = self.modelsList[self.index].books[self.tabViewList[self.index].row(item)].filepath
                os.startfile(filepath)
        except:
            self.statusbar.showMessage("Nie znaleziono programu odpowiedniego do otworzenia pliku", 2000)
            return

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

