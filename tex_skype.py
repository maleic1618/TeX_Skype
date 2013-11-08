#!/usr/bin/env python
#-*- coding:utf-8 -*-

import Skype4Py
import sys
import re
import time
import os
from PyQt4 import QtGui, QtCore, QtWebKit
from xml.sax.saxutils import *
from urllib import urlopen

class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.html = ''
        self.image_count = 0
        self.initUI()
        self.skype = Skype4Py.Skype()
        self.skype.OnMessageStatus = self.handler
        #self.skype.Attach()
        self.skype_thread = MyThread(self.skype)
        self.skype_thread.start()
        speaking_to_id = raw_input(u'Skype id whose you are speaking to:')
        self.chat = self.skype.CreateChatWith(speaking_to_id)
        self.show()

    def initUI(self):
        self.display_text = QtGui.QTextBrowser()
        self.input_text   = InputText(self)
        self.tex_text     = QtGui.QTextEdit()
        self.tex_image    = QtGui.QLabel()
        self.tex_widget   = QtGui.QWidget()

        self.input_text.setFixedHeight(80)
        self.tex_widget.setFixedHeight(100)
        self.tex_widget.setHidden(True)
        
        tex_layout = QtGui.QHBoxLayout()
        my_layout  = QtGui.QVBoxLayout()
        
        tex_layout.addWidget(self.tex_text)
        tex_layout.addWidget(self.tex_image)
        self.tex_widget.setLayout(tex_layout)

        my_layout.addWidget(self.display_text)
        my_layout.addWidget(self.input_text)
        my_layout.addWidget(self.tex_widget)
        my_layout.setMargin(5)
        
        self.setLayout(my_layout)

        self.setWindowTitle('TeX Skype')
        self.display_text.setHtml(self.html)
        self.input_text.setFocus()

    def handler(self, message, event):
        if event == u'RECEIVED':
            print 'RECEIVED'
            text = self.tex_replace(message.Body)
            print '!'
            self.html = self.html + unicode(message.FromDisplayName) + u':' + text +  u'<br>'
            self.display_text.setHtml(unicode(self.html))

        #self.moveToThread(QtGui.QApplication.instance().thread())

    def tex_replace(self, text):
        r1 = r'\$(.*?)\$'
        url = u'<img src="%s">'
        tex_code = re.compile(r1).findall(text)
        img_path = [self.tex_image_download(tex) for tex in tex_code]

        for tex, path in zip(tex_code, img_path):
            print tex, path
            text = text.replace('$'+tex+'$', url%path)
        
        return text

    def tex_image_download(self, tex):
        base_url = 'http://chart.apis.google.com/chart'
        url_ext = 'cht=tx&chl=' + tex
        opener = urlopen(base_url, url_ext.encode('utf-8'))
        img = opener.read()

        img_path = os.path.normpath(os.path.join(base_path, './tex-img/'+str(self.image_count)+'.png'))
        f=open(img_path, 'wb')
        f.write(img)
        self.image_count +=1
        return img_path
        
         
class InputText(QtGui.QTextEdit):
    def __init__(self, mw):
        super(InputText, self).__init__()
        self.mw = mw

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ControlModifier:
            self.mw.chat.SendMessage(unicode(self.toPlainText()))
            text = self.mw.tex_replace(unicode(self.toPlainText()))
            self.mw.html = self.mw.html + u'自分:' + text + u'<br>'
            print self.mw.html
            self.mw.display_text.setHtml(unicode(self.mw.html))
            self.setText('')

        if event.key() == QtCore.Qt.Key_Escape:
            self.setText('')

        return QtGui.QTextEdit.keyPressEvent(self, event)

class MyThread(QtCore.QThread):
    def __init__(self, skype):
        super(MyThread, self).__init__()
        self.skype = skype

    def run(self):
        self.skype.Attach()

if __name__ == '__main__':
    base_path = os.path.dirname(os.path.abspath(__file__))
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    app.exec_()
