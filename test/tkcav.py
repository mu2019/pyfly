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
NEWLINECHAR = '\n'


class TkEvent(object):
    def __init__(self,data,read_only=False):
        self.__dict__['__metadata__']=data
        self.__dict__['_ReadOnly']=read_only

    def __setitem__(self,item,value):
        self.__dict__['__metadata__'][item]=value

    def __getitem__(self,item):
        return self.__dict__['__metadata__'][item]

    def __getattr__(self,attr):
        return self.__dict__['__metadata__'].get(attr)

    def __setattr__(self,attr,value):
        if self.isReadOnly(): #__dict__['__metadata__'].get('ReadOnly') == True:
            return
        self.__dict__['__metadata__'][attr]=value

    def __delitem__(self,attr):
        self.__dict__['__metadata__'].pop(attr)

    def __delattr__(self,attr):
        self.__dict__['__metadata__'].pop(attr)

    def isReadOnly(self):
        return self.__dict__.get('_ReadOnly',False)

    def setReadOnly(self,read_only):
        self.__dict__['_ReadOnly'] = read_only

    def keys(self):
        return self.__dict__['__metadata__'].keys()

    def values(self):
        return self.__dict__['__metadata__'].values()

    def items(self):
        return self.__dict__['__metadata__'].items()

    def update(self,adict):
        if self.isReadOnly(): #__dict__['__metadata__'].get('ReadOnly') == True:
            return
        self.__dict__['__metadata__'].update(adict)

    def clear(self):
        self.__dict__['__metadata__'].clear()

    def __repr__(self):
        return 'TkEvent %s' % str(dict(self.__dict__['__metadata__']))

class EditorBase(tk.Canvas,_WidgetBase):
    def __init__(self,parent,*args,**kwargs):
        '''
        按键事件定义
        {char:字符,IME:启用输入法,IMEStr:输入法输入字符串,downkeysym:已按下的按键名称,keycode:按键id}
        IMESatae:-1未启用,0英文状态,1/2正在输入,3输入内容提交
            -1 --> 1 --> 2 --> 3 --> 0
            -1 --> 1 --> 3 --> 0 
        
        '''
        
        super(EditorBase,self).__init__(parent, *args, **kwargs)
        #_WidgetBase.__init__(self)
        #tk.Canvas.__init__(self,parent, *args, **kwargs)
        self._ItemBuffer = []
        self._IMEState = 0
        self._KeyPressBuffer = set() #[()]
        self._KeyPressEvent = {}
        self._KeyPressRawCode = {}
        self._KeyReleaseBuffer = []
        self._KeyReleaseEvent = {}
        #
        self._CursorLinePos = 0
        self._CursorCoordinat = [0,0]
        self._CursorCoordinatPixel = [0,0]

        self._DefaultFont = myFont=font.Font(family="msyh", size=14)
        self._CharWidth,self._LineHeight = self._DefaultFont.measure(' '),self._DefaultFont.metrics("linespace")

        #print('char width,height',self._CharWidth,self._LineHeight)

        self._Cursor= self.create_text(0,0,text='', anchor=NW, font=myFont)
        self.focus(self._Cursor)
        self.icursor(self._Cursor, 0)

        self.bind('<Key>',self.onKey)
        self.bind('<KeyPress>',self._onKeyPress)
        self.bind('<KeyRelease>',self._onKeyRelease)

    def _onKeyRelease(self,evt):

        #print('********key release**: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
        
        #,IME输入按键,IMEState=2
        #IMEState ==1 時,KeyRelease事件,正常事件值
        ## if self._IMEState == 1:
        ##     if evt.keycode == 0:
        ##         self._IMEState = 3
        ##     else:
        ##         self._IMEState = 2
        ##     self._KeyPressBuffer.remove('??')
        ## elif self._IMEState in (2,3):
        ##     pass
            
        pkevt = self._KeyPressEvent
        keysym = evt.keysym
        char = evt.char
        keycode = evt.keycode
        rawchar = char
        
        kevt=dict(self._KeyPressEvent)
        if '_L' in keysym  and keysym not in self._KeyPressBuffer:
            keysym = keysym.replace('_L','_R')
        '??' in self._KeyPressBuffer and self._KeyPressBuffer.remove('??')

        if evt.keycode in self._KeyPressRawCode:
            rawchar = self._KeyPressRawCode.pop(evt.keycode)
            keysym in self._KeyPressBuffer and self._KeyPressBuffer.remove(keysym)
            ## if (len(evt.keysym)==1 and evt.char != evt.keysym) :
            ##     char = ''

            if self._IMEState == 3:
                self._IMEState == 0
                char = ''
        elif self._KeyPressEvent['IME'] !=  -1:
            #print('keysym',keysym)
            #print('********key release**: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"',self._IMEState)
            #print('pkevt',pkevt)
            if self._IMEState == 3:
                keysym = pkevt['keysym']
                
            if keysym == 'BackSpace':
                char = ''
            #IME激活狀態
            #kevt['keycode'] = 0
            keycode = 0
            if  evt.keycode==0:
                self._IMEState = 3
            elif self._IMEState == 3: #pkevt['keycode'] == 229:
                self._IMEState = 0
                char = ''
                rawchar = evt.char #''
            else:
                self._IMEState = 2
                char = ''
                rawchar = evt.char #''
            
        else:
            char = ''
            
        downkeysym = ' %s ' % ' '.join(list(self._KeyPressBuffer))
        
        if (len(keysym)==1 and evt.char != keysym)  or  'Alt' in downkeysym:
            char = ''
            
        kevt['IME'] = self._IMEState
        kevt['keycode'] = keycode
        kevt['rawchar'] = rawchar
        kevt['char'] = char
        kevt['keysym'] = keysym
        kevt['downkeysym'] = downkeysym 
        kevt['event'] = 'keyrelease'
        kevt = TkEvent(kevt,True)
        self.after(0,self.onKeyRelease,kevt)

    def onKeyRelease(self,evt):
        pass
            
    def _onKeyPress(self,evt):
        #print('--key press--: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
        self._KeyPressBuffer.add(evt.keysym)
        #{char:字符,IME:输入法状态,downkeysym:已按下的按键名称,scancode:按键id,sym:按键名称,rawchar:ctrl等组合键的值}
        #是否为输入法启用状态
        #IME开始,IMEState=1
        #keycode == 229且keysym=='??' 或 char无值且keysym长度为1
        
        char , keycode , keysym = evt.char or '' , evt.keycode , evt.keysym
        rawchar = char
        kevt = {}
        if (evt.keycode == 229 and evt.keysym=='??') or  (not evt.char and len(evt.keysym)==1):
            self._IMEState = 1
            char = ''
        #,IME输入按键,IMEState=2
        #IMEState ==1 時,KeyRelease事件,正常事件值
        #输入IME字符,IMEState=3
        #char为输入内容,keycode==0,keysym=='??'
        elif evt.keycode == 0 and evt.keysym == '??':
            if self._KeyPressEvent['keycode'] != 299: # == 1: # and keysym == '??':
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
                char = '' # evt.keysym 同时ctrl键时不显示字符
                rawchar = evt.char

        self._KeyPressRawCode[keycode] = rawchar
        #char只是可显示的字符
                
        self._KeyPressEvent = kevt = {'char':char,
                'IME':self._IMEState,
                'keycode':keycode,
                'rawchar':rawchar,
                'keysym':keysym,
                'downkeysym':' %s ' % ' '.join(list(self._KeyPressBuffer))
                }
        
        if kevt['keycode'] != 229 and self._IMEState == 1:
            return
        kevt['event'] = 'keypress'
        kevt = TkEvent(kevt,True)
        #print('\tkpress evt',kevt)
        self.after(0,self.onKeyPress,kevt)

    def onKeyPress(self,evt):
        #print('key press',evt)
        pass
        
    def onKey(self,evt):
        #evt.char
        #print('--key--: char"',evt.char,'" keycode:"',evt.keycode,'" keysym:"',evt.keysym,'"')
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

class Editor(EditorBase):
    def __init__(self,parent,*args,**kwargs):
        super(Editor,self).__init__(parent,*args,**kwargs)
        self._CmdMap = {
            'InputText':self.textInput,
            'Up':self.cursorUp

            }
        self._KeyMap = {
            'Control+p':'Up'
            }
        


    def textInput(self,text):
        '''
        文字输入
        '''
        text = text[0]
        if text == NEWLINECHAR:
            self._CursorLinePos +=1
            self._CursorCoordinat[0] = 0
            self._CursorCoordinat[1] += 1
            self._CursorCoordinatPixel[0] = 0
            self._CursorCoordinatPixel[1] += self._LineHeight
            txt = self.create_text(self._CursorCoordinatPixel[0],self._CursorCoordinatPixel[1],text=text, anchor=NW, font=self._DefaultFont)
        elif text:
            width,height = self._DefaultFont.measure(text),self._DefaultFont.metrics("linespace")
            txt = self.create_text(self._CursorCoordinatPixel[0],self._CursorCoordinatPixel[1],text=text,font=self._DefaultFont,anchor='nw')
            self._CursorCoordinatPixel[0] += width
            self._CursorCoordinat[0] += 1
            self._CursorLinePos += 1
        self.coords(self._Cursor,tuple(self._CursorCoordinatPixel))
        self._ItemBuffer.append(txt)

    def cursorUp(self,evt=None):
        '''
        光標上移
        '''
        print('cursor up line pos',self._CursorLinePos)
        print('cursor up cordinat',self._CursorCoordinat)
        print('cursor up cordinat pixel',self._CursorCoordinatPixel)
        

    def cursorInput(self,cursor):
        '''
        光标控制输入
        '''
        pass

    def inputParse(self,evt):
        '''
        按鍵解釋為編輯指令
        '''
        if evt.char:
            char = NEWLINECHAR if evt.keysym == 'Return'  else evt.char
            cmd=  ('InputText',char)
        elif evt.keysym == 'Up':
            cmd = ('Up',)
        else:
            cmd = ('unknow',)
        return cmd
    

    def onKeyRelease(self,evt):
        print(' **** onkeyrelease **** ',evt)
        cmd = self.inputParse(evt)
        cmdfun = self._CmdMap.get(cmd[0])
        cmdfun and cmdfun(cmd[1:])
        ## char = evt.char
        ## if evt.char:
        ##     char = NEWLINECHAR if evt.keysym == 'Return'  else evt.char
        ##     self.textInput(char)
        #elif evt.keysym in ('Left','Right'
            

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

