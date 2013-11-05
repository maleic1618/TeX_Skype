#!/usr/bin/env python
#-*- coding:utf-8 -*-

import Skype4Py
import sys
import re
import time
from PyQt4 import QtGui, QtCore, QtWebKit
from xml.sax.saxutils import *

class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.html = ''
        self.initUI()
        self.skype = Skype4Py.Skype()
        self.skype.OnMessageStatus = self.handler
        self.skype_thread = MyThread(self.skype)
        self.skype_thread.start()
        speaking_to_id = raw_input(u'Skype id whose you are speaking to:')
        self.chat = self.skype.CreateChatWith(speaking_to_id)
        self.show()

    def initUI(self):
        self.display_text = QtWebKit.QWebView()
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
            text = tex_replace(message.Body)
            self.html = self.html + unicode(message.FromDisplayName) + u':' + text +  u'<br>'
            self.display_text.setHtml(unicode(self.html))
          
class InputText(QtGui.QTextEdit):
    def __init__(self, mw):
        super(InputText, self).__init__()
        self.mw = mw

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ControlModifier:
            self.mw.chat.SendMessage(unicode(self.toPlainText()))
            text = tex_replace(unicode(self.toPlainText()))
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

def tex_replace(text):
    r1 = r'\$([^$]*?)\$'
    r2 = r'<img src="http://www.codecogs.com/gif.latex?\1">'
    return re.sub(r1, r2, text)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    app.exec_()