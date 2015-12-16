#!/usr/bin/env python
# -*- coding:  utf-8 -*-

from ..misc.pylogging import log

class _WidgetBase(object):
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
