#!/usr/bin/env python
#!coding=utf-8 

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
import sys,re
import multiprocessing as mp
import inspector 
Signal=pyqtSignal
Slot=pyqtSlot


__keyworks__="and,as,assert,break,class,continue,def,del,elif,else,except,False,finally,for,from,global,if,import,in,is,lambda,None,not,or,pass,raise,return,True,try,while,with,yield,".split(',')
__builtinskeys__=dir(__builtins__)

'''
語法高亮方案
    關鍵字
    內置函數
    庫,類
    方法,函數
    錯誤名稱
    語法錯誤

多進程檢查語法,對象解析
根據語法檢查結果設置高亮

'''

class LineNumberArea(QWidget):
    
    def __init__(self,editor):
        super(LineNumberArea,self).__init__(editor)
        self.CodeEditor=editor

    def sizeHint(self):
        return QSize(self.CodeEditor.lineNumberAreaWidth(),0)

    def paintEvent(self,evt):
        self.CodeEditor.lineNumberAreaPaintEvent(evt)
        

class PfSyntaxStyle(QSyntaxHighlighter):
    newLineEnter=Signal(object)
    def __init__(self,parent=None):
        super(PfSyntaxStyle,self).__init__(parent)
        

    def highlightBlock(self,text):
        #print('highline block',text)
        #針對不同對象設置不同的高亮方案
        style=QTextCharFormat()
        style.setFontWeight(QFont.Bold)
        style.setForeground(Qt.darkMagenta)
        if len(text.strip())==1:
            self.newLineEnter.emit(text)
        for w in re.findall('\w+',text):
            if w in __keyworks__:
                m=re.search(w,text)
                if m:
                    self.setFormat(m.start(),m.end()-m.start(),style)
        

class PfEditor( QPlainTextEdit): #QTextEdit):
    def __init__(self,parent=None):
        super(PfEditor,self).__init__(parent)
        self._SyntaxStyle=PfSyntaxStyle(self.document())
        self.lineNumberArea=LineNumberArea(self)
        self.SyntaxCheckQueue=mp.Queue()
        self.SyntaxCheckQueueCome=mp.Queue()
        self.SyntaxCheckProc = mp.Process(target=inspector.SyntaxCheck, args=(self.SyntaxCheckQueue,self.SyntaxCheckQueueCome))
        self.SyntaxCheckProc.start()

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlineCurrentLine)
        
        self._SyntaxStyle.newLineEnter.connect(self.onNewLineEnter)
        self.updateLineNumberAreaWidth(0)
        self.highlineCurrentLine()


    def updateLineNumberAreaWidth(self,width):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0);
        #setViewportMargins(lineNumberAreaWidth(), 0, 0, 0);

    
    def updateLineNumberArea(self,rect,dy):
        if dy:
            self.lineNumberArea.scroll(0,dy)
        else:
            self.lineNumberArea.update(0,rect.y(),self.lineNumberArea.width(),rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def highlineCurrentLine(self):
        extraSelections=[]
        selection=QTextEdit.ExtraSelection()
        lineColor=QColor(Qt.yellow).lighter(160)
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection,True)
        selection.cursor=self.textCursor()
        selection.cursor.clearSelection()
        extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

        ## if (!isReadOnly()) {
        ##     QTextEdit::ExtraSelection selection;

        ##     QColor lineColor = QColor(Qt::yellow).lighter(160);

        ##     selection.format.setBackground(lineColor);
        ##     selection.format.setProperty(QTextFormat::FullWidthSelection, true);
        ##     selection.cursor = textCursor();
        ##     selection.cursor.clearSelection();
        ##     extraSelections.append(selection);
        ## }

        ## setExtraSelections(extraSelections);        


    def lineNumberAreaWidth(self):
        digits=1
        maxw=max(1,self.blockCount())
        while maxw>=10:
            maxw /= 10
            digits+=1
        space=5+self.fontMetrics().width('9') * digits;
        return space


    def resizeEvent(self,evt):
        QPlainTextEdit.resizeEvent(self,evt)
        cr=self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def onNewLineEnter(self,text):
        cur=self.textCursor()
        p=cur.position()
        code=self.toPlainText()
        ln=code[:p].count('\n')+1
        print('new line',cur,p,ln)
        self.SyntaxCheckQueue.put(('SYNTAXCHECK',ln,code))
        #pass
        
    def lineNumberAreaPaintEvent(self,event):
        painter=QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        block=self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top<=event.rect().bottom():
            if block.isVisible and bottom>=event.rect().top():
                number=str(int(blockNumber)+1)
                painter.setPen(Qt.black)
                painter.drawText(0,top,self.lineNumberArea.width()-2,self.fontMetrics().height(),Qt.AlignRight,number)
            block=block.next()
            top=bottom
            bottom=top+self.blockBoundingRect(block).height()
            blockNumber+=1


    def closeEvent(self,evt):
        self.SyntaxCheckProc.terminate()
        evt.accept()


def main():
    
    p=sys.argv[1] if len(sys.argv)>1 else ''
    app=QApplication(sys.argv)
    #app.setStyle('fusion')
    #QApplication.setStyle(QStyleFactory.create("Cleanlooks"))
    #QApplication.setPalette(QApplication.style().standardPalette())
    win=PfEditor()
    #win=MWin(None,kws.get('plugin'),kws.get('setting'))
    win.show()
    sys.exit(app.exec_())
    pass

if __name__=='__main__':
    main()
    
