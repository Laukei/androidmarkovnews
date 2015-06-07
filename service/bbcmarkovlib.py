#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import copy
import random

start_string = '**START**'
end_string = '**END**'
max_sentence_length = 100 #words

def processUrl(url_address):
	print 'updating source data'
	titledata = []
	descdata = []
	url = urllib2.urlopen(url_address)
	data = url.read().split('\n')
	url.close()

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

def genSetOfWords(sentences):
	wordlist = []
	for sentence in sentences:
		wordlist += sentence.split(' ')
	print len(wordlist),'input words;',len(wordlist)-len(set(wordlist)),'overlaps (more is better)'
	return sorted(list(set(wordlist)))

def genMarkov(sentences,wordset):
	prototype = {}
	for word in ([start_string]+wordset+[end_string]):
		prototype[word]=0
	markov_graph = copy.deepcopy(prototype)
	for key in prototype.keys():
		markov_graph[key] = copy.deepcopy(prototype)
	for sentence in sentences:
		sentence = sentence.split(' ')
		for w, word in enumerate(sentence):
			if w == 0:
				markov_graph[start_string][word]+=1
			try:
				markov_graph[word][sentence[w+1]]+=1
			except IndexError:
				markov_graph[word][end_string]+=1
	return markov_graph

def selectFromMarkov(word,markov_graph):
	total = sum(markov_graph[word].values())
	running_total = 0
	value = random.randint(0,total)
	for k, key in enumerate(sorted(markov_graph[word].keys())):
		if markov_graph[word][key]!=0:
			running_total += markov_graph[word][key]
			if running_total>=value:
				return key

def genSentence(markov_graph):
	sentence_composites = [selectFromMarkov(start_string,markov_graph)]
	i = 0
	while True:
		i+=1
		sentence_composites.append(selectFromMarkov(sentence_composites[-1],markov_graph))
		if sentence_composites[-1]==end_string or i>max_sentence_length:
			break
	return sentence_composites

def processSentence(sentence_composites):
	sentence = sentence_composites[0]
	for composite in sentence_composites[1:-1]:
		sentence+=' '+composite
	return sentence



	

