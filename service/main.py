from time import sleep, asctime, localtime
from kivy.lib import osc
from kivy.network.urlrequest import UrlRequest
import bbcmarkovlib as bml
from kivy.clock import Clock

serviceport = 3000
activityport = 3001

def some_api_callback(message, *args):
	print("got a message! %s" % message)
	if message[2] == 'UPDATE_DB':
		update_db(message[3])
	elif message[2] == 'GENERATE':
		generate_sentence()

def processUrlData(url_data):
	print 'updating source data'
	titledata = []
	descdata = []
	data = url_data.split('\n')

	for d, datum in enumerate(data):
		data[d]=datum.strip()
	for row in data:
		if row.find('<title>') == 0:
			title = row[7:-8]
			if title != 'BBC News - Home':
				titledata.append(title)
		if row.find('<description>') == 0:
			description = row[13:-14]
			if description != 'The latest stories from the Home section of the BBC News web site.':
				descdata.append(description)
	return titledata,descdata

def process_result(result):
	osc.sendMsg('/some_api', ['UPDATE_DB','progress','downloaded data...', ], port=activityport)
	titledata, descdata = processUrlData(result)
	descdataset = bml.genSetOfWords(descdata)
	titledataset = bml.genSetOfWords(titledata)
	osc.sendMsg('/some_api', ['UPDATE_DB','progress','created datasets...', ], port=activityport)
	markov_graph = bml.genMarkov(descdata,descdataset)
	osc.sendMsg('/some_api', ['UPDATE_DB','progress','created description set...', ], port=activityport)
	markov_title = bml.genMarkov(titledata,titledataset)
	osc.sendMsg('/some_api', ['UPDATE_DB','progress','created headline set...', ], port=activityport)
	#self.ids.random_number.text = str(result[500:800])
	return markov_title, markov_graph

markov_graph = []
markov_title = []
def on_success(req,result):
	#self.ids.update_time.text = 'updated: processing...'
	global markov_graph
	global markov_title
	markov_title, markov_graph = process_result(result)
	osc.sendMsg('/some_api', ['UPDATE_DB','success',asctime(localtime()), ], port=activityport)
	print 'success'
	
def on_fail(req,result):
	osc.sendMsg('/some_api', ['UPDATE_DB','fail',asctime(localtime()), ], port=activityport)
	print 'failed'
	#self.ids.update_time.text = str('updated: FAILURE, are you connected to the internet?')

def update_db(url_address,*args):
	#self.ids.update_time.text = 'updated: downloading...'
	UrlRequest(url_address, on_success, on_fail).wait()

def gen_sentence_from_markov(graph):
	try:
		for i in range(10): # try 10 times (REALLY BAD WAY TO STOP UNICODEENCODEERROR)
			try:
				sentence_bits = bml.genSentence(graph)
				sentence = str(bml.processSentence(sentence_bits))
				return sentence
			except UnicodeEncodeError:
				pass
	except AttributeError:
		osc.sendMsg('/some_api',['GENERATE','fail','you can\'t generate one until you UPDATE_DB','FAILURE'],port=activityport)
		return None
	osc.sendMsg('/some_api',['GENERATE','fail','stuck escaping unicode (python2.7 sucks at unicode)','FAILURE'],port=activityport)
	return None

def generate_sentence(*args):
	sentence_desc = gen_sentence_from_markov(markov_graph)
	sentence_title = gen_sentence_from_markov(markov_title)
	if sentence_desc != None and sentence_title != None:
		osc.sendMsg('/some_api',['GENERATE','success',sentence_title,sentence_desc],port=activityport)

if __name__ == '__main__':
	osc.init()
	oscid = osc.listen(ipAddr='127.0.0.1', port=serviceport)
	osc.bind(oscid, some_api_callback, '/some_api')
	while True:
		osc.readQueue(oscid)
		sleep(.1)
		#Clock.tick()