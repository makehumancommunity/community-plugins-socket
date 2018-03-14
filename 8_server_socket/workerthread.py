#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman server socket plugin

**Product Home Page:** TBD

**Code Home Page:**    TBD

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin opens a TCP socket and accepts some basic commands. It 
does not make much sense without a corresponding client.

"""

import gui3d
import mh
import gui
import socket
import json

from core import G

mhapi = gui3d.app.mhapi

qtSignal = None
qtSlot = None

if mhapi.utility.isPython3():
    from PyQt5 import QtGui
    from PyQt5 import QtCore
    from PyQt5.QtGui import *
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    qtSignal = QtCore.pyqtSignal
    qtSlot = QtCore.pyqtSlot
else:
    if mhapi.utility.isPySideAvailable():
        from PySide import QtGui
        from PySide import QtCore
        from PySide.QtGui import *
        from PySide.QtCore import *
        qtSignal = QtCore.Signal
        qtSlot = QtCore.Slot
    else:
        from PyQt4 import QtGui
        from PyQt4 import QtCore
        from PyQt4.QtGui import *
        from PyQt4.QtCore import *
        qtSignal = QtCore.pyqtSignal
        qtSlot = QtCore.pyqtSlotmhapi = G.app.mhapi

QThread = mhapi.ui.QtCore.QThread

from .dirops import SocketDirOps
from .meshops import SocketMeshOps
from .modops import SocketModifierOps

class WorkerThread(QThread):

    signalAddMessage = qtSignal(str)
    signalEvaluateCall = qtSignal()

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False
        self.log = mhapi.utility.getLogChannel("socket")

    def addMessage(self,message,newLine = True):
        self.signalAddMessage.emit(message)
        print(message)
        pass

    def run(self):
        self.addMessage("Opening server socket... ")        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('127.0.0.1', 12345))
        except socket.error as msg:
            self.addMessage('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] + "\n")
            return;

        self.addMessage("opened at port 12345\n")        

        self.socket.listen(10)

        while not self.exiting:
            self.addMessage("Waiting for connection.")        

            try:
                conn, addr = self.socket.accept()
    
                if conn and not self.exiting:
                    self.addMessage("Connected with " + addr[0] + ":" + str(addr[1]))
                    data = conn.recv(8192)
                    self.addMessage("Client says: '" + data + "'")
                    data = gui3d.app.mhapi.internals.JsonCall(data)
    
                    self.jsonCall = data
                    self.currentConnection = conn
    
                    self.signalEvaluateCall.emit()
            except socket.error:
                """Assume this is because we closed the socket from outside"""
                pass

    def stopListening(self):
        if not self.exiting:
            self.addMessage("Stopping socket connection")
            self.exiting = True
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                """If the socket was not connected, shutdown will complain. This isn't a problem, 
                so just ignore."""
                pass
            self.socket.close()

    def __del__(self):        
        self.stopListening()



