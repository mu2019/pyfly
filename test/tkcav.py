#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from pylogging import log


#from tkevents import TkEventLoop
#import threading

import time
import sys,re
import multiprocessing as mp
import inspector
from PIL import Image, ImageTk

from _WidgetBase import _WidgetBase


SEPARATOR = '~!@#$%^&*()+`{}[]:"|;\'\\<>?,./ \n\r\t'
LOWERCHR = ['a','z'] #ord('a'),ord('z')]
UPERCHR = ['A','Z'] #ord('A'),ord('Z')]
UNICODECHR = ['\u1000','\uFFFE']
NUMBERCHR = ['0','9']


class Editor(tk.Canvas,_WidgetBase):
    def __init__(self,parent,*args,**kwargs):
        super(Editor,self).__init__(parent, *args, **kwargs)
        #tk.Canvas.__init__(self,parent, *args, **kwargs)
        self._Buffer = []
        #
        self._CursorLinePos = 0
        self._CursorCoordinat = [0,0]
        self._CursorCoordinatPixel = [0,0]

        self._DefaultFont = myFont=font.Font(family="msyh", size=14)

        txt = self.create_text(0,0,text='', anchor=NW, font=myFont)
        self.focus(txt)
        self.icursor(txt, 0)

        self.bind('<Key>',self.onKeyPress)
        
    def onKeyPress(self,evt):
        #evt.char
        print('--key--',evt.char,evt.keycode,evt.keysym)
        if evt.keysym in ('BackSpace','Delete'):
            print('delete')
        elif evt.char and self.isVisibleChar( evt.char):
            #width = self._DefaultFont.measure(evt.char)
            width,height = self._DefaultFont.measure(evt.char),self._DefaultFont.metrics("linespace")
            t = self.create_text(self._CursorCoordinatPixel[0],self._CursorCoordinatPixel[1],text=evt.char,font=self._DefaultFont,anchor='nw')
            self._CursorCoordinatPixel[0] += width
            self._CursorCoordinat[0] += 1
            self._CursorLinePos += 1
            #print(self._CursorCoordinat[0])
            self._Buffer.append(t)
            #print('code',ord(evt.char),width)
            self.focus(t)
            self.icursor(t, 1)

    def isVisibleChar(self,char):
        return char in SEPARATOR  \
               or LOWERCHR[0] <= char <= LOWERCHR[-1]  \
               or UPERCHR[0] <= char <= UPERCHR[-1] \
               or UNICODECHR[0] <= char <= UNICODECHR[-1] \
               or NUMBERCHR[0] <= char <= NUMBERCHR[-1]


class Example(tk.Frame):
    #
    def __init__(self, parent,*args, **kwargs):
        tk.Frame.__init__(self,parent, *args, **kwargs)
        #highlightthickness=0, relief='ridge'
        canvas = self.text = Editor(self,takefocus='tab',highlightthickness=0, relief='ridge') #tk.Canvas(self)
        self.vsb = ttk.Scrollbar(orient="vertical", command=self.text.yview)
        self.hsb = ttk.Scrollbar(orient="horizontal", command=self.text.xview)
        self.Parent = parent
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        #self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)
        canvas.focus_set()
        #myText="" #blahablah"
        #txt = canvas.create_text(10,10,text=myText, anchor=NW, font=myFont)

        # place the cursor on the fifth character
        
        #canvas.focus(txt)
        #canvas.icursor(txt, 2)

        # get the position
        #print( "cursor character position=",canvas.index(txt, INSERT))

        # Find the pixel bounds of the insertion cursor
        #  (assume 1 pixel width of the cursor)

        ## text=myText[0:canvas.index(txt, INSERT)]
        ## width=myFont.measure(text)
        ## bbox=canvas.bbox(txt)
        ## x1=bbox[0]+width-1
        ## y1=bbox[1]
        ## x2=x1+1
        ## y2=bbox[3]
        #canvas.create_rectangle(x1,y1,x2,y2, outline="red")

        #self.text.bind('<Key>',self.onKeyPress)
        parent.protocol("WM_DELETE_WINDOW", self.onClosing)


    def onClosing(self):
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            #self.SyntaxCheckProc.terminate()

            self.Parent.destroy()
            self.Parent.quit()
        


if __name__ == "__main__":
    root = tk.Tk()
    #root.title('易飞ERP系统 ver: 9')
    print('root',root,type(root))
    app=Example(root)
    app.pack(side="top", fill="both", expand=True)
    root.mainloop()
    
    #root = tk.Tk()
    
    #print('app',app)
    #print('Starting on thread', threading.get_ident())
    #app.mainloop()
    ## loop = TkEventLoop(app)
    ## app.loop = loop
    ## loop.mainloop()

