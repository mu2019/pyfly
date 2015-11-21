#!/usr/bin/env python
#!coding=utf-8

import inspect

INFO_NONE=0
INFO_ERROR=1
INFO_WARNING=2
INFO_ALL=3


class pylogging_meta(type):
    log_level=INFO_ALL
    def set_log_level(cls,level):
        pylogging_meta.log_level=level

    def log(cls,*mes):
        cfr=inspect.currentframe()
        cr=inspect.getouterframes(cfr)[1]
        mess=str(mes)[1:-1]
        if isinstance(mes,tuple) and len(mes)==1:
            mess=mess[:-1]
        print('__pylogging__ %s@%s >> ' % (cr[1],cr[2]),mess)

class pylogging(metaclass=pylogging_meta):
    def __init__(self):
        super(pyloggin,self).__init__()

log=pylogging.log
set_log_level=pylogging.set_log_level

