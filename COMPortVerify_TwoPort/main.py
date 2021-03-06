"""Subclass of MainFrame, which is generated by wxFormBuilder."""

import wx
import GUI
import logging
from COMPort import *
from common import *
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(message)s',
                    datefmt="%H:%M:%S",
                    filename='logger.log',
                    filemode='w')
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(logging.Formatter('%(asctime)s:%(message)s' , "%Y-%m-%d %H:%M:%S"))
logging.getLogger().addHandler(streamHandler)
UpdateCOMPortUsage()
# Implementing MainFrame
class MainFrame( GUI.MainFrame ,ThreadingManagement):
    def __init__( self, parent ):
        GUI.MainFrame.__init__( self, parent )
        ThreadingManagement.__init__(self)
        for port in gCOMUsage.keys():
            if(not gCOMSerial.port and not gCOMUsage[port]):
                self.m_choice_Port1.Append(port)
                self.m_choice_Port1.SetSelection(0)
                gCOMSerial.connect(port)
            elif(not gCOMBT.port and not gCOMUsage[port]):
                self.m_choice_Port2.Append(port)
                self.m_choice_Port2.SetSelection(0)
                gCOMBT.connect(port)
            elif(not gCOMUsage[port]):
                self.m_choice_Port1.Append(port)
                self.m_choice_Port2.Append(port)
         
    def OnSize( self, event ):
        logging.debug(self.GetSizeTuple())
    def OnChoicePort( self, event ):
        port1 = self.m_choice_Port1.GetStringSelection()
        port2 = self.m_choice_Port2.GetStringSelection()
        logging.debug("m_choice_Port1=%s" % port1)
        logging.debug("m_choice_Port2=%s" % port2)
        self.m_choice_Port1.Clear()
        self.m_choice_Port2.Clear()
        self.m_choice_Port1.Append(port1)
        self.m_choice_Port1.SetSelection(0)
        gCOMSerial.connect(port1)
        self.m_choice_Port2.Append(port2)
        self.m_choice_Port2.SetSelection(0)
        gCOMBT.connect(port2)
        for port in gCOMUsage.keys():
            if(port == port1 or port == port2):
                continue
            else:
                self.m_choice_Port1.Append(port)
                self.m_choice_Port2.Append(port)
    def OnBtnClickExe( self, event ):
        if(self.thrd_stop_done):
            for child in self.GetChildren():
                if(not isinstance(child,wx.Button) and not isinstance(child,wx.StaticText)):
                    child.Enable(False)
            self.m_btn_Exe.SetLabel(u"Stop")
            self.ThreadStart(self.ThreadRun)
        else:
            self.ThreadStop()
            self.m_btn_Exe.SetLabel(u"Start")
    def ThreadRun(self):
        gCOMSerial.timeout = self.m_spinCtrlTime.GetValue()/1000.0
        gCOMBT.timeout = self.m_spinCtrlTime.GetValue()/1000.0
        Port1Err  = 0
        Port1Send = 0
        Port1Recv = 0
        Port2Err  = 0
        Port2Send = 0
        Port2Recv = 0
        xferLen = self.m_spinCtrlLen.GetValue()
        Port1Data = bytearray(xferLen)
        Port2Data = bytearray(xferLen)
        for i in range(self.m_spinCtrlLen.GetValue()):
            Port1Data[i] = i&0xFF
            Port2Data[i] = (i&0xFF)^0xFF
        while(not self.thrd_stop):
            nByte = gCOMSerial.write(list(Port1Data))
            logging.debug("[%s] wr %d" % (gCOMSerial.portstr,nByte))
            Port1Send +=1
            if(nByte!=xferLen):
                Port1Err += 1
            nByte = gCOMBT.read(xferLen)
            logging.debug("[%s] rd %d" % (gCOMBT.portstr,len(nByte)))
            Port2Recv +=1
            if(len(nByte)!=xferLen or bytearray(nByte)!=Port1Data):
                logging.debug(ByteArrayToStr(bytearray(nByte)))
                Port2Err += 1
            self.m_st_Port1Send.SetLabel("%d" % Port1Send)
            self.m_st_Port1Recv.SetLabel("%d" % Port1Recv)
            self.m_st_Port1Err.SetLabel("%d" % Port1Err)
            self.m_st_Port2Send.SetLabel("%d" % Port2Send)
            self.m_st_Port2Recv.SetLabel("%d" % Port2Recv)
            self.m_st_Port2Err.SetLabel("%d" % Port2Err)
            self.Refresh()
            time.sleep(self.m_spinCtrlTime.GetValue()/1000.0)
            if(self.thrd_stop):
                break
            nByte = gCOMBT.write(list(Port2Data))
            logging.debug("[%s] wr %d" % (gCOMBT.portstr,nByte))
            Port2Send +=1
            if(nByte!=xferLen):
                Port2Err += 1
            nByte = gCOMSerial.read(xferLen)
            logging.debug("[%s] rd %d" % (gCOMSerial.portstr,len(nByte)))
            Port1Recv +=1
            if(len(nByte)!=xferLen or bytearray(nByte)!=Port2Data):
                logging.debug(ByteArrayToStr(bytearray(nByte)))
                Port1Err += 1
            self.m_st_Port1Send.SetLabel("%d" % Port1Send)
            self.m_st_Port1Recv.SetLabel("%d" % Port1Recv)
            self.m_st_Port1Err.SetLabel("%d" % Port1Err)
            self.m_st_Port2Send.SetLabel("%d" % Port2Send)
            self.m_st_Port2Recv.SetLabel("%d" % Port2Recv)
            self.m_st_Port2Err.SetLabel("%d" % Port2Err)
            self.Refresh()
            time.sleep(self.m_spinCtrlTime.GetValue()/1000.0)
        self.ThreadDone()
if __name__=='__main__':
    app = wx.App()
    my_frame = MainFrame(None)
    my_frame.Show()
    app.MainLoop()