#!/usr/bin/env python
# -*- coding :  utf-8 -*-
"""
Some text
hello
"""
import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
from pylogging import log
#from tkconstants import RIGHT, LEFT, Y, BOTH

from tkevents import TkEventLoop
#import threading

import time
import sys,re
import multiprocessing as mp
import inspector
from PIL import Image, ImageTk


__keywords__="and,as,assert,break,class,continue,def,del,elif,else,except,False,finally,for,from,global,if,import,in,is,lambda,None,not,or,pass,raise,return,True,try,while,with,yield,".split(',')
__builtinskeys__=dir(__builtins__)

color_style={'keyword':{'foreground':"purple"},
             "classname":{'foreground':"forest green"},
             "string":{'foreground':"sienna"},
             'function':{'foreground':'navy'},
             'number':{'foreground':'yellow4'},
             'buildin':{'foreground':'DeepSkyBlue3'},
             'sel':{'foreground':'black',
                    'background':'gray92'}
             }

#詞語分隔符,
SEPARATOR = '~!@#$%^&*()+`{}[]:"|;\'\\<>?,./ \n\r\t'
LOWERCHR = ['a','z'] #ord('a'),ord('z')]
UPERCHR = ['A','Z'] #ord('A'),ord('Z')]
UNICODECHR = ['\u1000','\uFFFE']
NUMBERCHR = ['0','9']
NAMECHR = [LOWERCHR,UPERCHR,UNICODECHR,['_'],NUMBERCHR]
NAMESTARTCHR = [LOWERCHR,UPERCHR,UNICODECHR,['_']]
#namechr='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
#numchr='1234567890'
NEWLINECHR = '\n\r' #[ord('\n'),ord('\r')]


class Widget_Proxy(object):
    def __init__(self):

        self.tk.createcommand('WidgetCommand',self._WidgetCommand)
        
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {
                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]
                #eval  "WidgetCommand $widget [join $args { }]"

                after 0 [WidgetCommand  $widget  [list $args]]
                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))
    

    def _WidgetCommand(self,*args):
        log('**_widget ** ',args)
        paras=args[1]
        cmd=[args[0]]
        self.tk.eval("set cmd_list  %s" % paras)
        result = [ self.tk.eval("lindex $cmd_list %d" % i)
                   for i in range(int(self.tk.eval("llength $cmd_list")))]
        cmd.extend(result)
        self.widgetCommand(*cmd)

        
    def widgetCommand(self,*args):
        pass
    
'''
data={"one": 1, "two": 2}

widget.bind("<ButtonPress-1>", lambda event, arg=data: self.on_mouse_down(event, arg))
'''

class TextLineNumbers(tk.Canvas):
    """
    行號自動適應寬度
    """
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.width=kwargs.get('width',30)
        #(w,h) = (font.measure(text),font.metrics("linespace"))        

    def attach(self, text_widget):
        ## if self.textwidget:
        ##     self.textwidget.unbind("<MouseWheel>")
        ##     # with Linux OS
        ##     self.textwidget.unbind("<Button-4>")
        ##     self.textwidget.unbind("<Button-5>")
        
        self.textwidget = text_widget
        #windows
        ## self.textwidget.bind("<MouseWheel>", self.delaydraw)
        ## # with Linux OS
        ## self.textwidget.bind("<Button-4>", self.delaydraw)
        ## self.textwidget.bind("<Button-5>", self.delaydraw)
        self.textwidget.bind("<<LineCountChanged>>", self.delaydraw)
        self.textwidget.bind("<<DrawLineNumber>>", self.delaydraw)

    def delaydraw(self,*args):
        self.after(0,self.redraw,*args)


    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")
        w=self.textwidget.winfo_height()
        #log(w)
        i = self.textwidget.index("@0,0")
        j = 0 #self.textwidget.index("@0,end")
        #log('#'*8,i,j,self.textwidget._CursorPos)
        while True :
            dline= self.textwidget.dlineinfo(i)
            width=self.textwidget.winfo_width()

            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            fill='red' if int(linenum)==self.textwidget._CursorPos[0] else 'black'
            #log('line',linenum,dline,width,self.textwidget['width'])

            self.create_text(10,y,anchor="nw", text=linenum,width=self.width,fill=fill)
            i = self.textwidget.index("%s+1line" % i)

class CustomText(tk.Text,Widget_Proxy): #ModifiedMixin,
    '''
    undo,redo,縮進分級線
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        Widget_Proxy.__init__(self)
        self._TotalLine=0
        self._CursorPos=[0,0]
        self._LastWord = [0,0]
        self._Blocking=False
        i=self.dlineinfo('0.0')
        fnt=font.Font(font=self['font'])
        dir(fnt)
        #log('line info',i,fnt,fnt.measure('9'),fnt.metrics('linespace'))
        image = Image.open("outline.png")
        image = image.crop((0,0,1,fnt.metrics('linespace')))
        self._IndentLineImage=ImageTk.PhotoImage(image)        
        self.image_create('1.4',image=self._IndentLineImage)
        #self.tag_config("CurrentLine", background="light yellow")         
        #super(CustomText,self).__init__(*args,**kwargs)
        self.loadStyle()

    def getPos(self):
        return tuple(self._Pos)

    def loadStyle(self):
        """
        載入配色方案
        """
        for k,v in color_style.items():
            log('*'*8,'color style',k,v)
            self.tag_config(k,**v)

    def setColorTag(self,cmd):
        '''
        設置列表中每一個詞的tag
        15-11-18
        設置目前修改的詞的配色
        增加:
            一般文字namechar,
            分隔符,
        '''
        txt=self.get('%s.%s' % (self._CursorPos[0],0),'%s.end' % self._CursorPos[0])
        curword = ''
        
        
        if cmd[1] == 'insert':
            c = cmd[-1]
            if c in NEWLINECHR:
                #new line
                pass
            elif True in [r[0] <= c <= r[-1] for r in NAMECHR]:
                #name char
                log('name char',self._CursorPos)

                pass
            else:
                #symbol
                log('last word',self._LastWord)
                pass
            #isnamechr = (True in [r[0] <= c <= r[1] for r in namechr])
            
        elif cmd[0] == 'delete':
            pass
                
        log(txt)

    def cursorWord(self):
        
        pass
            

    def highlineCurrentLine(self):
        #self.tag_delete('CurrentLine')
        rng=self.tag_ranges("sel")
        hln=[]
        cline=self._CursorPos[0]        
        if len(rng)==2:
            log('sel range',rng) #sel_start,sel_end)
            sel_rng=rng
            
            sel_start=[int(p) for p in str(rng[0]).split('.')]
            sel_end=[int(p) for p in str(rng[1]).split('.')]
            lns=self.get(rng[0],rng[1]).split('\n')
            log('*'*8,sel_start,sel_end,lns)
            if sel_start[0]==cline and sel_start[1]>0:
                hln.append(("%s.0" % sel_start[0],"%s.%s" % tuple(sel_start)))
            #elif sel_start[0]==self._CursorPos[0]: # and sel_start[1]=0:
            if sel_end[0]==cline:
                ltext=self.get('%s.0' % cline ,'%s.end' % cline)
                log('line text',ltext)
                
                hln.append(("%s.%s" % tuple(sel_end),"%s.%s" % (sel_end[0],len(ltext)+1)))
            log(hln)
            for r in hln:
                self.tag_add("CurrentLine",r[0],r[1])
        else:
            self.tag_add("CurrentLine", "%s.0" % cline, "%s.0+1lines" % cline)

    def lineCountIsChange(self,cmd):
        if cmd[1]=='insert':

            if '\n' in cmd[-1]:
                self.event_generate("<<LineCountChanged>>",when='tail')
            elif cmd[-1]=='\x08':
                self.delete('insert-1c')
        elif cmd[1]=='delete':
            totalline=self.index('end').split('.')[0]

            if totalline!=self._TotalLine:
                self.event_generate("<<LineCountChanged>>",when='tail')
                self._LineCount=totalline


    def cursorPositionChange(self,cmd):
        #log(cmd,cmd[1:4], cmd[1:4] == ('mark','set','insert'))
        if cmd[1:4] == ('mark','set','insert'):
            pos =[int(c) for c in cmd[4].split('.')]
        else:
            pos=[int(c) for c in self.index('insert').split('.')]
        self._CursorPos=pos
        #log('cursor position',pos)
        if pos[0]!=self._CursorPos[0]:
            self.tag_remove("CurrentLine", "@%s,0" % self._CursorPos[0], "%s.0+1lines" % self._CursorPos[0])
            #self._CursorPos=pos
            self.event_generate("<<DrawLineNumber>>",when='tail')
            #self.event_generate("<<LineCountChanged>>",when='tail')
            #self.after(0,self.highlineCurrentLine)

    def lineWrap(self,cmd):
        '''
        
        '''
        if cmd[1] not in ('insert','delete') and self['wrap'] == 'none':
            return
        w=self['width']
        i=int(self.index('1.end').split('.')[1])
        if i>w:
            self.event_generate("<<DrawLineNumber>>",when='tail')

    def widgetCommand(self,*cmd):
        #log(cmd)
        if cmd[1] in ('insert','delete','mark'):
            self.lineCountIsChange(cmd)
            self.cursorPositionChange(cmd)
            self.lineWrap(cmd)
            self.setColorTag(cmd)
            ## if cmd[1] in ('insert','delete'):#,'mark'):
            ##     t=self.get('%s.%s' % (self._CursorPos[0],0),'%s.end' % self._CursorPos[0])
            ##     log('line text',self._CursorPos,t)
        elif cmd[1] in ('yview'):
            self.event_generate("<<DrawLineNumber>>",when='tail')
        #print(self.index('insert'))
            

        
    def beenModified(self, event=None):
        '''
        Override this method do do work when the Text is modified.
        '''
        pass

    def delay_yview(self,*args):
        #res = self.tk.call(self._w, 'xview', *args)
        print('delay yview',self,args)
        self.tk.call(self._w, 'yview', 'scroll', int(args[1]),args[2])

class Example(tk.Frame):
    def __init__(self, parent,*args, **kwargs):
        tk.Frame.__init__(self,parent, *args, **kwargs)

        self.Parent=parent
        self.text = CustomText(self,wrap='char')
        
        
        #print(self.text.yview)
        self.vsb = ttk.Scrollbar(orient="vertical", command=self.text.yview)
        self.hsb = ttk.Scrollbar(orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=self.vsb.set,xscrollcommand=self.hsb.set)
        self.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
        self.linenumbers = TextLineNumbers(self, width=30)
        self.linenumbers.attach(self.text)

        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        #self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self.linenumbers.redraw) #_on_change)
        #self.vsb.bind("<MouseWheel>", self._onMouseWheel)

        ## self.text.insert("end", "one\ntwo\nthree\n")
        ## self.text.insert("end", "four",("bigfont",))
        ## self.text.insert("end", " and four 2\n")
        ## self.text.insert("end", "five\n")
        ## #改变指定文本字体
        ## self.text.tag_add("bigfont",'2.0', '2.2')

        parent.protocol("WM_DELETE_WINDOW", self.onClosing)

    def onClosing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            #self.SyntaxCheckProc.terminate()
            self.Parent.destroy()
            

    def _on_change(self, event):
        self.linenumbers.redraw()

        
if __name__ == "__main__":
    root = tk.Tk()
    #root.title('易飞ERP系统 ver: 9')
    print('root',root,type(root))
    app=Example(root)
    app.pack(side="top", fill="both", expand=True)
    #root.mainloop()
    
    #root = tk.Tk()
    
    print('app',app)
    #print('Starting on thread', threading.get_ident())
    #app.mainloop()
    loop = TkEventLoop(app)
    app.loop = loop
    loop.mainloop()

    
    
#from ScrolledText import ScrolledText

## def example():
##     import __main__
##     #from Tkconstants import END

##     stext = ScrolledText(bg='white', height=10)
##     stext.insert(END, __main__.__doc__)

##     f = font.Font(family="times", size=30, weight="bold")
##     stext.tag_config("font", font=f)
##     stext.insert(END, "Hello", "font")
##     stext.pack(fill=BOTH, side=LEFT, expand=True)
##     stext.focus_set()
##     stext.mainloop()

'''
Ok,

The following code demonstrates:

a) finding the char index  of the insertion cursor in a text item in a Canvas
b) translating that char position into pixel position
c) drawing a box around the insertion cursor.

Did I miss something?


from Tkinter import *
from tkFont import Font

root=Tk()

canvas=Canvas(root)
canvas.pack()
myFont=Font(family="Times", size=14)

myText="blahblah"
txt = canvas.create_text(10,10,text=myText, anchor=NW, font=myFont)

# place the cursor on the fifth character
canvas.focus_set()
canvas.focus(txt)
canvas.icursor(txt, 5)

# get the position
print "cursor character position=",canvas.index(txt, INSERT)

# Find the pixel bounds of the insertion cursor
#  (assume 1 pixel width of the cursor)

text=myText[0:canvas.index(txt, INSERT)]
width=myFont.measure(text)
bbox=canvas.bbox(txt)
x1=bbox[0]+width-1
y1=bbox[1]
x2=x1+3
y2=bbox[3]
canvas.create_rectangle(x1,y1,x2,y2, outline="red")

root.mainloop()
'''
