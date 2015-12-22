#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox

from PIL import ImageTk,Image,ImageDraw,ImageFont


## class EditorBase(tk.Canvas,_WidgetBase):
##     def __init__(self,parent,*args,**kwargs):
##         pass

#class ControlBox(tk.

def main():
    
    pass

#import Tkinter as tk

class GradientFrame(tk.Canvas):
    '''A gradient frame which uses a canvas to draw the background'''
    def __init__(self, parent, borderwidth=1, relief="sunken"):
        tk.Canvas.__init__(self, parent, borderwidth=borderwidth, relief=relief)
        self._color1 = "red"
        self._color2 = "black"
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        '''Draw the gradient'''
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = width
        (r1,g1,b1) = self.winfo_rgb(self._color1)
        (r2,g2,b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
            self.create_line(i,0,i,height, tags=("gradient",), fill=color)
        self.lower("gradient")

def circle(radius):
    "Bresenham complete circle algorithm in Python"
    # init vars
    switch = 3 - (2 * radius)
    points = set()
    x = 0
    y = radius
    # first quarter/octant starts clockwise at 12 o'clock
    while x <= y:
        # first quarter first octant
        points.add((x,-y))
        # first quarter 2nd octant
        points.add((y,-x))
        # second quarter 3rd octant
        points.add((y,x))
        # second quarter 4.octant
        points.add((x,y))
        # third quarter 5.octant
        points.add((-x,y))        
        # third quarter 6.octant
        points.add((-y,x))
        # fourth quarter 7.octant
        points.add((-y,-x))
        # fourth quarter 8.octant
        points.add((-x,-y))
        if switch < 0:
            switch = switch + (4 * x) + 6
        else:
            switch = switch + (4 * (x - y)) + 10
            y = y - 1
        x = x + 1
    return points

class Button(tk.Canvas):
    def __init__(self, parent):
        pass

class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        w = Canvas(self, width=200, height=200)
        #self.wm_overrideredirect(True)
        #gradient_frame = GradientFrame(self,borderwidth=0)
        #gradient_frame.pack(side="top", fill="both", expand=True)
        cp = circle(5)
        
        #print('circle',cp)
        #w.create_arc((0,10,50,50),style='arc')
        w.pack(side="top", fill="both", expand=True)
        for p in cp:
            if p[0]>0 and p[1]>0:
                #1quadrant
                pass
            elif p[0]<0 and p[1]>0:
                #2quadrant
                pass
            elif p[0]<0 and p[1]<0:
                #3quadrant
                pass
            elif p[0]>0 and p[1]<0:
                #4quadrant
                pass
            w.create_line(p[0]+51,p[1]+51,p[0]+52,p[1]+52)
        ## inner_frame = tk.Frame(gradient_frame)
        ## inner_frame.pack(side="top", fill="both", expand=True, padx=8, pady=(16,8))

        b1 = ttk.Button(self, text="Close",command=self.destroy)
        ## t1 = tk.Text(inner_frame, width=40, height=10)
        b1.pack(side="top")
        #t1.pack(side="top", fill="both", expand=True)

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()

## if __name__ == '__main__':
##     main()


