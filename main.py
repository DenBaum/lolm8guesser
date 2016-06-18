import os, sys, logging, ConfigParser
from PySide import QtGui, QtWebKit
from jinja2 import Template
from riotwatcher import LoLException
from friendship import *

scriptPath = os.path.realpath(os.path.dirname(__file__))
log = logging.getLogger('log')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

configFilePath = os.path.join(scriptPath, 'config.cfg')
config = ConfigParser.ConfigParser()
config.read(configFilePath)
apiKey = config.get('SummonerData', 'api_key')
summonerName = config.get('SummonerData', 'summoner_name')
past10 = config.getboolean('Algorithm', 'include_past_10_normal_matches')

if not config.getboolean('Algorithm', 'debug'):
	log.setLevel(logging.CRITICAL)

premades = None
try:
	premades = getPremades(summonerName, apiKey, past10)
	pass
except LoLException as e:
	app = QtGui.QApplication(sys.argv)
	msgbox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, u"Error", str(e).decode('utf8'))
	msgbox.exec_()
	
if premades != None:
	app = QtGui.QApplication(sys.argv)
	geo = QtGui.QDesktopWidget().screenGeometry()
	
	templateString = open(os.path.join(scriptPath,'templates','main.html')).read().decode('utf8')
	template = Template(templateString)
	
	webwindow = QtWebKit.QWebView()
	webwindow.move(int(geo.width()/2)-int(300/2), int(geo.height()/2)-int(200/2))
	webwindow.setWindowTitle(u'DenBaum ist der coolste')
	webwindow.resize(300,200)
	webwindow.setHtml(template.render(premades=premades))
	webwindow.show()
	
	app.exec_()