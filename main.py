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
from kivy.graphics import Color, Rectangle
from kivy.metrics import Metrics
from kivy.uix.progressbar import ProgressBar

import random
import time

url_address = 'http://feeds.bbci.co.uk/news/rss.xml'
activityport = 3001
serviceport = 3000

class FirstScreen(Screen):
	bgcolor = [1,1,1,1]
	textcolor = [0.25,0.25,0.25,1]
	buttoncolor = [5/8.,1,0.25,1]
	buttontextcolor = [1,1,1,1]


class SecondScreen(Screen):
	pass

class MyScreenManager(ScreenManager):
	pass

class AndroidApp(App):
	def build(self):
		if platform == 'android':
			self.start_service()
			from jnius import autoclass
			self.Locale = autoclass('java.util.Locale')
			self.PythonActivity = autoclass('org.renpy.android.PythonActivity')
			self.TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
			self.tts = self.TextToSpeech(self.PythonActivity.mActivity, None)
			self.locales = {
				'CANADA':self.Locale.CANADA,
				'FRANCE':self.Locale.FRANCE,
				'GERMANY':self.Locale.GERMANY,
				'ITALY':self.Locale.ITALY,
				'JAPAN':self.Locale.JAPAN,
				'KOREA':self.Locale.KOREA,
				'CHINA':self.Locale.SIMPLIFIED_CHINESE,
				'UK':self.Locale.UK,
				'US':self.Locale.US
				}
		osc.init()
		oscid = osc.listen(ipAddr='127.0.0.1', port=activityport)
		osc.bind(oscid, self.some_api_callback, '/some_api')
		Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)
		self.service_enabled = False
		self.toggle_service()
		self.load_settings()
		self.chosen_locale = self.config.get('example','optionsexample')
		self.tts_enabled = bool(int(self.config.get('example','boolexample')))
		return

	def load_settings(self,*args):
		from default_settings import settings_defaults
		self.loaded_settings = settings_defaults

	def build_config(self,config):
		config.setdefaults('example',{
			'boolexample':True,
			'optionsexample':'UK',
			'stringexample': url_address
			})

	def build_settings(self,settings):
		settings.add_json_panel('Skim Read News',
			self.config,
			data=self.loaded_settings)
		self.use_kivy_settings = False

	def on_config_change(self,config,section,key,value):
		#print config,section,key,value
		if key == 'boolexample':
			self.tts_enabled = bool(int(value))
		if key == 'stringexample':
			self.url_address = value
		if key == 'optionsexample':
			self.chosen_locale = value

	def update_db(self,*args):
		osc.sendMsg('/some_api',['UPDATE_DB',url_address,],port=serviceport)
		self.root.current_screen.ids.generator.disabled = True
		self.root.current_screen.ids.update_time.text = 'updating... (takes a while)'
		self.root.current_screen.ids.downloader.disabled = True
		self.root.current_screen.ids.downloader.text = 'Downloading...'

	def generate_sentence(self,*args):
		osc.sendMsg('/some_api',['GENERATE',],port=serviceport)

	def read_sentence(self,*args):
		if platform == 'android':
			self.tts.setLanguage(self.locales[self.chosen_locale])
			self.tts.speak(self.root.current_screen.ids.headline.text, text.TextToSpeech.QUEUE_FLUSH, None)
			self.tts.speak(self.root.current_screen.ids.random_number.text, self.TextToSpeech.QUEUE_ADD, None)
		print 'read:',self.root.current_screen.ids.headline.text,self.root.current_screen.ids.random_number.text

	def on_pause(self):
		return True

	def on_resume(self):
		return

	def some_api_callback(self, message, *args):
		print("got a message! %s" % message)
		#print self.root.current_screen.ids
		if message[2] == 'UPDATE_DB':
			if message[3] == 'success' and self.service_enabled == True:
				self.root.current_screen.ids.update_time.text = 'updated: '+str(message[4])
				self.root.current_screen.ids.generator.disabled = False
				self.root.current_screen.ids.downloader.disabled = False
				self.root.current_screen.ids.downloader.text = 'Download'
			elif message[3] == 'success' and self.service_enabled == False:
				self.root.current_screen.ids.downloader.text = 'Download'
			elif message[3] == 'progress':
				self.root.current_screen.ids.update_time.text = message[4]
			elif message[3] == 'fail':
				self.root.current_screen.ids.update_time.text = 'update failed, are you connected to the net?'
		elif message[2] == 'GENERATE':
			self.root.current_screen.ids.random_number.text = str(message[5])
			self.root.current_screen.ids.headline.text = str(message[4])
			if self.tts_enabled == True:
				self.read_sentence()

	def stop_service(self,*args):
		if platform == 'android':
			self.service.stop()
		self.service_enabled = False

	def start_service(self,*args):
		if platform == 'android':
			from android import AndroidService
			service = AndroidService('SRN Service','Generating you great headlines')
			service.start('service started')
			self.service = service
		self.service_enabled = True

	def toggle_service(self,*args):
		if self.service_enabled == True:
			self.stop_service()
			self.root.current_screen.ids.toggler.background_color = [1,5/8.,.25,1]
			self.root.current_screen.ids.toggler.text = 'Service OFF'
			self.root.current_screen.ids.downloader.disabled = True
			self.root.current_screen.ids.generator.disabled = True
		else:
			self.start_service()
			self.root.current_screen.ids.toggler.background_color = [5/8.,1,0.25,1]
			self.root.current_screen.ids.toggler.text = 'Service ON'
			self.root.current_screen.ids.downloader.disabled = False
			self.root.current_screen.ids.generator.disabled = True
			


if __name__ == "__main__":
	AndroidApp().run()