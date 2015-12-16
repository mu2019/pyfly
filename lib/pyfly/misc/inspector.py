#!/usr/bin/env python
#!coding=utf-8

import ast
import asyncio


_syntaxModel=None

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

class SyntaxCheck():
    def __init__(self):
        self.SyntaxCheckInQueue=mp.Queue()
        self.SyntaxCheckOutQueue=mp.Queue()
        self.SyntaxCheckProc = mp.Process(target=self._syntaxCheck, args=(self.SyntaxCheckInQueue,self.SyntaxCheckOutQueue))

    def __del__(self):
        try:
            self.SyntaxCheckProc.terminate()
        except:
            pass

    def start():
        self.SyntaxCheckProc.start()
        
    def _syntaxCheck(sources,outgo):
        '''
        語法錯誤檢查
        soruces,請求來源隊列Queue,(檢查類型,當前行號,檢查代碼)
        outgo,結果返回列表Queue,(檢查類型,當前行號,檢查結果)

        '''
        global _syntaxModel
        while 1:
            req,line,source=sources.get()
            print(req,source)
            if req=='SYNTAXCHECK':
                result=None
                try:
                    l={}
                    cc=compile(source,'','exec') #{},l,'exec')
                    exec(cc,{},l)
                    _syntaxModel=l

                except Exception as e:
                    print(e)
                    result=e
                outgo.put((req,line, result))
            elif req=='AUTOCOMPLETE':
                source.strip()

            elif req == 'CURSORWORD':
                '''
                get word at cursor
                '''
                pass
    
