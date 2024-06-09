import sys
import requests
import io
import os

from dccon import DcCON

from PyQt6.QtCore import (
     QSize,
     QByteArray,
     QBuffer,
     QIODeviceBase,
     


     
)
from PyQt6.QtGui import (
     QPixmap,
     QIcon,
     QMovie
     
)
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QMainWindow,
    QLineEdit,
)


# DcCON Extend
class DcCON(DcCON):
    def dcconlist(self, dccon_id):
        pkg_idx = ''.join(filter(str.isalnum, str(dccon_id)))
        url = self.url_download
        headers = self.headers_download

        data = self._get_package_data(pkg_idx)
        info, detail = data['info'], data['detail']

        result = []

        for i, pkg in enumerate(detail):
                params = { 'no': pkg['path'] }
                image = requests.get(url, headers=headers, params=params, stream=True)
                ext = pkg.get('ext', 'png')
                result.append((io.BytesIO(image.content),ext))
        return result


            
class MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()

        self.swindow = None
        self.test = 0

        self.setWindowTitle("DC Con")
        pagelayout = QVBoxLayout()
        buttonlayout = QHBoxLayout()
        self.detaillayout = QGridLayout()

        pagelayout.addLayout(buttonlayout)
        pagelayout.addLayout(self.detaillayout)

        favbtn = QPushButton("favorite")
        #sortbtn = QComboBox()
        self.searchdetailbtn = QLineEdit()
        self.searchdetailbtn.returnPressed.connect(self.search)
        searchbtn = QPushButton('search')
        searchbtn.clicked.connect(self.search)

        self.dcconlist = []

        #sortbtn.addItem('Hottest')
        #sortbtn.addItem('Newest')        
        
        buttonlayout.addWidget(favbtn)
        #buttonlayout.addWidget(sortbtn)
        buttonlayout.addWidget(self.searchdetailbtn)
        buttonlayout.addWidget(searchbtn)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def search(self):
        
        self.resetlayout(self.detaillayout)
        searchdetail = self.searchdetailbtn.text()
        searchresult = DcCON().search(searchdetail)
        for link, thumbnail, name, author in searchresult:
            row = self.detaillayout.count() // 5
            col = self.detaillayout.count() % 5
            self.detaillayout.addWidget(self.createdcconbtn(link,thumbnail,name,author),row,col)

    def createdcconbtn(self,link,thumbnail,name,author):
        
        
        testcopy = name
        #btnlayout = QVBoxLayout()
        def makesubwindow():
            self.swindow = SubWindow(link,name)
            self.swindow.show()
        testbtn = QPushButton()
        testbtn.setFixedHeight(100)
        testbtn.setFixedWidth(100)
        testbtn.setIconSize(QSize(100,100))
        image = QPixmap()
        image.loadFromData(thumbnail.read())
        icon = QIcon()
        icon.addPixmap(image)
        testbtn.setIcon(icon)
        testbtn.clicked.connect(makesubwindow)

        btnname = QLabel(str(testcopy))
        btnname.setParent(testbtn)

        
        #btnlayout.addWidget(testbtn)
        #btnlayout.addWidget(btnname)
        

        return testbtn
    
    def resetlayout(self,layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    
class SubWindow(QWidget):

    def __init__(self,link,name):
        super().__init__()
        self.setWindowTitle(name)
        contents = DcCON().dcconlist(link[1:])
        self.mainlayout = QGridLayout()
        self.label = QLabel(link[1:])

        for image, ext in contents:
            row = self.mainlayout.count() // 5
            col = self.mainlayout.count() % 5
            self.mainlayout.addWidget(self.createbtn(image,ext),row,col)
        self.setLayout(self.mainlayout)
    def createbtn(self,img,ext):
        image = img.read()
        
        
        
        if ext == 'gif':
            btn = self.gifbtn(image)
        else:
            btn = QPushButton()
            pimg = QPixmap()
            pimg.loadFromData(image)
            ico = QIcon()
            ico.addPixmap(pimg)
            btn.setIcon(ico)
        
        def imgtoclipboard(image,ext):
            with open(f'./dump.{ext}','r+b') as file:
                file.write(image)
                command = f'powershell Set-Clipboard -LiteralPath ./dump.{ext}'
                os.system(command)
                # url = QUrl.fromLocalFile(f'./dump.{ext}')
                # mimedata = QMimeData()
                # mimedata.setData(f'image/*',file.read())

                # cb = QApplication.clipboard()
                # cb.setMimeData(mimedata)


            # a = QByteArray(image)
            # print(image)
            # qmime = QMimeData()
            # qmime.setData(f'image/{ext}',image)
            # # qmime.setImageData(a)
            # cb = QApplication.clipboard()
            # cb.clear()
            # cb.setMimeData(qmime)


        # btn = QPushButton()
        # pimg = QPixmap()
        # print(image)
        # pimg.loadFromData(image)
        # ico = QIcon()
        # ico.addPixmap(pimg)
        # btn.setIcon(ico)
        btn.setFixedHeight(100)
        btn.setFixedWidth(100)
        btn.setIconSize(QSize(100,100))
        btn.clicked.connect(lambda : imgtoclipboard(image,ext))
        return btn
    
    def gifbtn(self,image) -> QPushButton:
        
        a = QByteArray(image)
        b = QBuffer(a)
        b.open(QIODeviceBase.OpenModeFlag.ReadOnly)
        gif = QMovie(b)
        
        
        
        
        btn = QPushButton()
        btn.setIcon(QIcon())
        
        def updateicon():
            btn.setIcon(QIcon(gif.currentPixmap()))
        gif.frameChanged.connect(updateicon)
        if gif.loopCount() != -1:
            gif.finished.connect(gif.start)
        gif.start()
        
        
        return btn

    def resetlayout(self,layout):
        while layout.count() > 0:
            layout.removeItem(layout.itemAt(layout.count()))



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
