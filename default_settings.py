import json

settings_defaults = json.dumps([
	{'type':'title',
	'title':'App settings'},
	{'type':'bool',
	'title':'TTS Enabled',
	'desc':'Enable Text-to-Speech for generated phrases',
	'section':'example',
	'key':'boolexample'},
	{'type':'options',
	'title':'TTS Locale',
	'desc':'Sets the locale of the Text-to-Speech voice',
	'section':'example',
	'key':'optionsexample',
	'options':['CANADA','CHINA','FRANCE','GERMANY','ITALY','JAPAN','KOREA','UK','US']},
	{'type':'string',
	'title':'Source URL',
	'desc':'URL to pull news headlines from',
	'section':'example',
	'key':'stringexample'},
	])