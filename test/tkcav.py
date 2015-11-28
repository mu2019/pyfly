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
        self._IMEState = 0
        self._KeyPressBuffer = set() #[()]
        self._KeyPressEvent = {}
        self._KeyReleaseBuffer = []
        self._KeyReleaseEvent = {}
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
        self.bind('<KeyPress>',self._onKeyPress)
        self.bind('<KeyRelease>',self._onKeyRelease)
        '''
        按键事件定义
        {char:字符,IME:启用输入法,IMEStr:输入法输入字符串,downkeysym:已按下的按键名称,keycode:按键id,

                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" k " keycode:" 75 " keysym:" k "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" m " keycode:" 77 " keysym:" m "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 员 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 员 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "              
        '''

    def _onKeyRelease(self,evt):
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
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" l " keycode:" 76 " keysym:" l "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 国 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 国 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "

                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" k " keycode:" 75 " keysym:" k "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" m " keycode:" 77 " keysym:" m "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 员 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 员 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "

                输入过程中字母上屏
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" a " keycode:" 65 " keysym:" a "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" b " keycode:" 66 " keysym:" b "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" c " keycode:" 67 " keysym:" c "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" a " keycode:" 0 " keysym:" ?? "
                **key release**: char" a " keycode:" 0 " keysym:" ?? "
                --key press--: char" b " keycode:" 0 " keysym:" ?? "
                **key release**: char" b " keycode:" 0 " keysym:" ?? "
                --key press--: char" c " keycode:" 0 " keysym:" ?? "
                **key release**: char" c " keycode:" 0 " keysym:" ?? "
                 " keycode:" 13 " keysym:" Return "
 
                输入过程中按ctrl
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" l " keycode:" 76 " keysym:" l "
                --key press--: char"  " keycode:" 17 " keysym:" Control_L "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char"  " keycode:" 77 " keysym:" m "
                **key release**: char"  " keycode:" 17 " keysym:" Control_L "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 国 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 国 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "

                --key press--: char"  " keycode:" 17 " keysym:" Control_L "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char"  " keycode:" 77 " keysym:" m "
                --key press--: char"  " keycode:" 76 " keysym:" l "
                --key press--: char"  " keycode:" 0 " keysym:" ?? "
                **key release**: char"  " keycode:" 0 " keysym:" ?? "
                **key release**: char"  " keycode:" 76 " keysym:" l "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char"  " keycode:" 77 " keysym:" m "
                **key release**: char"  " keycode:" 17 " keysym:" Control_L "
                 
                连续输入
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 际 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 际 " keycode:" 0 " keysym:" ?? "
                --key press--: char" 法 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 法 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "

                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" v " keycode:" 86 " keysym:" v "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" b " keycode:" 66 " keysym:" b "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 好 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 好 " keycode:" 0 " keysym:" ?? "
                **key release**: char"   " keycode:" 32 " keysym:" space "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" w " keycode:" 87 " keysym:" w "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" a " keycode:" 65 " keysym:" a "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                **key release**: char" d " keycode:" 68 " keysym:" d "
                --key press--: char"  " keycode:" 229 " keysym:" ?? "
                --key press--: char" 代 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 代 " keycode:" 0 " keysym:" ?? "
                --key press--: char" 码 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 码 " keycode:" 0 " keysym:" ?? "
                **key release**: char" c " keycode:" 67 " keysym:" c "
                
                輸入數字
                --key press--: char"  " keycode:" 51 " keysym:" 3 "
                --key press--: char" 3 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 3 " keycode:" 0 " keysym:" ?? "
                **key release**: char" 3 " keycode:" 51 " keysym:" 3 "
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

        進入虛擬輸入狀態
        --key press--: char"  " keycode:" 229 " keysym:" ?? "
        退出虛擬輸入狀態
        **key release**: char"  " keycode:" 76 " keysym:" l "
        keycode == ord(keysym)
        '''
        print('**key release**: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
        
        #,IME输入按键,IMEState=2
        #IMEState ==1 時,KeyRelease事件,正常事件值
        if self._IMEState == 1:
            if evt.keycode == 0:
                self._IMEState = 3
            else:
                self._IMEState = 2
            self._KeyPressBuffer.remove('??')
        elif self._IMEState in (2,3):
            pass
            
        kevt = self._KeyPressEvent
        
        kevt = {'char':char,
                'IME':self._IMEState,
                'keycode':evt.keycode,
                'keysym':evt.keysym,
                'downkeysym':' %s ' % ' '.join(list(self._KeyPressBuffer))
                }

    def _onKeyPress(self,evt):
        print('--key press--: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
        self._KeyPressBuffer.(evt.keysym)
        #{char:字符,IME:输入法状态,downkeysym:已按下的按键名称,scancode:按键id,sym:按键名称,rawchar:ctrl等组合键的值}
        #是否为输入法启用状态
        #IME开始,IMEState=1
        #keycode == 229且keysym=='??' 或 char无值且keysym长度为1
        rawchar = ''
        char , keycode , keysym = evt.char or '' , evt.keycode , evt.keysym
        kevt = {}
        if (evt.keycode == 229 and evt.keysym=='??') or  (not evt.char and len(evt.keysym)==1):
            self._IMEState = 1
            char = ''
        #,IME输入按键,IMEState=2
        #IMEState ==1 時,KeyRelease事件,正常事件值
        #输入IME字符,IMEState=3
        #char为输入内容,keycode==0,keysym=='??'
        elif evt.keycode == 0 and evt.keysym == '??':
            if self._KeyPressEvent['keycode'] ！＝ 299: # == 1: # and keysym == '??':
                #启用IME时按ctrl键组合时有charcode生成
                keycode = self._KeyPressEvent['keycode']
                keysym = self._KeyPressEvent['keysym']
                rawchar = char
                char = ''

            self._IMEState = 3
        #,IME结束,IMEState=0
        #输入IME字符后,IME字符最后上屏,KeyRelease事件
        else:
            #IME禁用
            self._IMEState = -1
            if len(evt.keysym)==1 and ord(evt.char) != ord(evt.keysym):
                char = evt.keysym
                rawchar = evt.char
                
        self._KeyPressEvent = kevt = {'char':char,
                'IME':self._IMEState,
                'keycode':keycode,
                'keysym':keysym,
                'downkeysym':' %s ' % ' '.join(list(self._KeyPressBuffer))
                }
        
        if kevt['keycode'] != 229 and self._IMEState == 1:
            return
        
        print(kevt)
        
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

