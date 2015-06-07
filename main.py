from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from kivy.clock import Clock
from kivy.lib import osc

import random
import time

url_address = 'http://feeds.bbci.co.uk/news/rss.xml'
activityport = 3001
serviceport = 3000


class FirstScreen(Screen):
	def update_db(self,*args):
		osc.sendMsg('/some_api',['UPDATE_DB',url_address,],port=serviceport)

	def generate_sentence(self,*args):
		osc.sendMsg('/some_api',['GENERATE',],port=serviceport)
'''
	def generate_sentence(self,*args):
		try:
			self.ids.random_number.text = str(bml.processSentence(bml.genSentence(self.markov_graph)))
		except AttributeError:
			self.ids.random_number.text = str('you can\'t generate one until you UPDATE_DB')
'''
class SecondScreen(Screen):
	pass

class MyScreenManager(ScreenManager):
	pass

class AndroidApp(App):
	def build(self):
		if platform == 'android':
			self.start_service()
		osc.init()
		oscid = osc.listen(ipAddr='127.0.0.1', port=activityport)
		osc.bind(oscid, self.some_api_callback, '/some_api')
		Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)
		return

	def on_pause(self):
		return True

	def on_resume(self):
		return

	def some_api_callback(self, message, *args):
		print("got a message! %s" % message)
		print self.root.current_screen.ids
		if message[2] == 'UPDATE_DB':
			if message[3] == 'success':
				self.root.current_screen.ids.update_time.text = 'updated: '+str(message[4])
			elif message[3] == 'fail':
				self.root.current_screen.ids.update_time.text = 'update failed, are you connected to the net?'
		elif message[2] == 'GENERATE':
			self.root.current_screen.ids.random_number.text = str(message[4])

	def stop_service(self,*args):
		self.service.stop()

	def start_service(self,*args):
		from android import AndroidService
		service = AndroidService('SRN Service','Generating you great headlines')
		service.start('service started')
		self.service = service


if __name__ == "__main__":
	AndroidApp().run()