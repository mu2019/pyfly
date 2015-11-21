#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from pyfly.misc.pylogging import log


#from tkevents import TkEventLoop
#import threading

import time
import sys,re
import multiprocessing as mp
import pyfly.misc.inspector as inspector
from PIL import Image, ImageTk

from pyfly.ui._WidgetBase import _WidgetBase


SEPARATOR = '~!@#$%^&*()+`{}[]:"|;\'\\<>?,./ \n\r\t'
LOWERCHR = ['a','z'] #ord('a'),ord('z')]
UPERCHR = ['A','Z'] #ord('A'),ord('Z')]
UNICODECHR = ['\u1000','\uFFFE']
NUMBERCHR = ['0','9']


class Editor(tk.Canvas,_WidgetBase):
    def __init__(self,parent,*args,**kwargs):
        super(Editor,self).__init__(parent, *args, **kwargs)
        #tk.Canvas.__init__(self,parent, *args, **kwargs)
        self._ItemBuffer = []
        self._KeyPressBuffer = [()]
        self._KeyReleaseBuffer = []
        #
        self._CursorLinePos = 0
        self._CursorCoordinat = [0,0]
        self._CursorCoordinatPixel = [0,0]

        self._DefaultFont = myFont=font.Font(family="msyh", size=14)
        self._CharWidth,self._LineHeight = self._DefaultFont.measure(' '),self._DefaultFont.metrics("linespace")

        print('char width,height',self._CharWidth,self._LineHeight)

        txt = self.create_text(0,0,text='', anchor=NW, font=myFont)
        self.focus(txt)
        self.icursor(txt, 0)

        self.bind('<Key>',self.onKey)
        self.bind('<KeyPress>',self.onKeyPress)
        self.bind('<KeyRelease>',self.onKeyRelease)

    def onKeyRelease(self,evt):
        '''
        按键对应
        英文状态
            keypress和keyrelease的keysym是对应的
            按下control键后char不对应
            --key press--: char"  " keycode:" 17 " keysym:" Control_L "
            --key press--: char"  " keycode:" 75 " keysym:" k "
            **key release**: char"  " keycode:" 75 " keysym:" k "
            --key press--: char"  " keycode:" 75 " keysym:" k "
            **key release**: char"  " keycode:" 75 " keysym:" k "
            **key release**: char"  " keycode:" 17 " keysym:" Control_L "            
        输入法开启情况下
            中文状态
                **key release**: char" l " keycode:" 76 " keysym:" l "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 国 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 国 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "
                连续输入
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 际 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 际 " keycode:" 0 " keysym:" ?? "
                --key press--: char" 法 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 法 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "                
           英文状态
               --key press--: char"  " keycode:" 74 " keysym:" j "
               --key press--: char" j " keycode:" 0 " keysym:" ?? "
               **key release**: char" j " keycode:" 0 " keysym:" ?? "
               **key release**: char" j " keycode:" 74 " keysym:" j "
               CONTROL
--key press--: char"  " keycode:" 17 " keysym:" Control_L "
--key press--: char"  " keycode:" 229 " keysym:" ?? "
**key release**: char"  " keycode:" 74 " keysym:" j "
--key press--: char"  " keycode:" 76 " keysym:" l "
--key press--: char"  " keycode:" 0 " keysym:" ?? "
**key release**: char"  " keycode:" 0 " keysym:" ?? "
**key release**: char"  " keycode:" 76 " keysym:" l "
**key release**: char"  " keycode:" 17 " keysym:" Control_L "

--key press--: char"  " keycode:" 17 " keysym:" Control_L "
--key press--: char"  " keycode:" 76 " keysym:" l "
--key press--: char"  " keycode:" 0 " keysym:" ?? "
**key release**: char"  " keycode:" 0 " keysym:" ?? "
**key release**: char"  " keycode:" 76 " keysym:" l "
**key release**: char"  " keycode:" 17 " keysym:" Control_L "

        '''
        print('**key release**: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
        keys = (evt.char,evt.keycode,evt.keysym)
        if keys not in self._KeyPressBuffer:
            pass
        else:
            self._KeyPressBuffer.remove(keys)
        print(self._KeyPressBuffer)

    def onKeyPress(self,evt):
        print('--key press--: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
        keys = (evt.char,evt.keycode,evt.keysym)
        if keys in self._KeyPressBuffer: # != keys and evt.keysym != '??' and evt.keycode != 229:
            self._KeyPressBuffer.append(keys)
        print(self._KeyPressBuffer)
        
        
    def onKey(self,evt):
        #evt.char
        print('--key--: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
        #char = evt.char evt.keycode>0 
        if evt.keysym in ('BackSpace','Delete'):
            print('delete')
        elif evt.char and ord(evt.char.upper()) != evt.keycode and evt.keycode:
            print('control key')
        elif evt.keysym == 'Return': #and evt.keycode in (10,13):
            print('return',evt.keycode)
            self._CursorLinePos +=1
            self._CursorCoordinat[0] += 0
            self._CursorCoordinat[1] += 1
            self._CursorCoordinatPixel[0] = 0
            self._CursorCoordinatPixel[1] += self._LineHeight
            txt = self.create_text(self._CursorCoordinatPixel[0],self._CursorCoordinatPixel[1],text='\n', anchor=NW, font=self._DefaultFont)
            self.focus(txt)
            self.icursor(txt, 0)
            self._ItemBuffer.append(txt)
        elif evt.char and self.isVisibleChar( evt.char):
            #width = self._DefaultFont.measure(evt.char)
            width,height = self._DefaultFont.measure(evt.char),self._DefaultFont.metrics("linespace")
            print('__char width,height',width,height)
            t = self.create_text(self._CursorCoordinatPixel[0],self._CursorCoordinatPixel[1],text=evt.char,font=self._DefaultFont,anchor='nw')
            self._CursorCoordinatPixel[0] += width
            self._CursorCoordinat[0] += 1
            self._CursorLinePos += 1
            #print(self._CursorCoordinat[0])
            self._ItemBuffer.append(t)
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

