"""Subclass of Main, which is generated by wxFormBuilder."""

import wx
import FrameMainBase
import time
import threading

myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)
class CountEvent(wx.PyCommandEvent):
		"""Event to signal that a count value is ready"""
		def __init__(self, etype, eid, value=None):
			"""Creates the event object"""
			wx.PyCommandEvent.__init__(self, etype, eid)
			self._value = value

		def GetValue(self):
			"""Returns the value from the event.
			@return: the value of this event
			"""
			return self._value

class CountingThread(threading.Thread):
		def __init__(self, parent):
			"""
			@param parent: The GUI object that should receive the value
			 """
			threading.Thread.__init__(self)
			self._parent = parent
			self._break  = False
			self._stop   = False

		def run(self):
			"""Overrides Thread.run. Don't call this directly its called internally
			when you call Thread.start().
			"""
			while(not self._stop):
				while(not self._break and not self._stop):
					time.sleep(2)
					self._value = 2
					evt = CountEvent(myEVT_COUNT, -1, self._value)
					wx.PostEvent(self._parent, evt)
				
				while(self._break and not self._stop):
					time.sleep(1)

# Implementing Main
class FrameMain( FrameMainBase.Main ):
	def __init__( self, parent ):
		FrameMainBase.Main.__init__( self, parent )
		self.m_btn_Run.Enable()
		self.Bind(EVT_COUNT, self.OnCount)
		self.worker = CountingThread(self)
		self.worker.start()		

	def __del__(self):
		self.worker._break = True
		self.worker._stop = True
		while(self.worker.is_alive()):
			time.sleep(0.5)		
	# Handlers for Main events.
	def OnBtnRun_Click( self, event ):
		# TODO: Implement OnBtnRun_Click
		self.m_btn_Run.Disable()
		val = int(self.m_staticText.GetLabel()) + 1
		self.m_staticText.SetLabel(unicode(val))
		self.worker._break = False
		self.worker._stop = False
		self.m_btn_Run.Enable()
		pass

	def OnBtnBreak_Click( self, event ):
		self.worker._break = True
		pass
	
	def OnBtnStop_Click( self, event ):
		self.worker._stop = True
		while(self.worker.is_alive()):
			time.sleep(0.5)
		pass
			
	def OnCount( self, event ):
		val = int(self.m_staticText.GetLabel()) + event.GetValue()
		self.m_staticText.SetLabel(unicode(val))
			
if __name__=='__main__':
	app = wx.App()
	my_frame = FrameMain(None)
	my_frame.Show()
	app.MainLoop()	
	del app