 # -*- coding: utf-8 -*-
import requests
from BeautifulSoup import BeautifulSoup
from conf import *

class SysacadSession:
	"Sesión de SysCAD."

	url = URLS_DICT

	def __init__(self, legajo=None, password=None, base_url=DEFAULT_BASE_URL):
		self.base_url = base_url
		self.login_data = {
			'legajo': legajo,
			'password': password,
		}

	def _get(self, url_action):
		self.login()
		url = self.base_url + url_action
		return requests.get(url, cookies=self.cookies) 

	def _post(self, url_action, data):
		self.login()
		url = self.base_url + url_action
		return requests.post(url, cookies=self.cookies, data=data)

	def login(self):

		# Make request
		url = self.base_url + self.url['login']
		response = requests.post(url, data=self.login_data)

		# Handle incorrect login
		html = BeautifulSoup(response.text)
		if html.title.string == u'Ingreso Alumnos al SYSACAD' or html('p', attrs={'class': "textoError"}):
			raise Exception('Información de login incorrecta.')

		# Store session cookie
		self.cookies = {SESSION_COOKIE_NAME: response.cookies[SESSION_COOKIE_NAME]}

	def _getInfoFromTable(self, url):
		response = self._get(self.url['materias_plan'])
		html = BeautifulSoup(response.text)
		trs = []
		for tr in html('tr', attrs={'class': "textoTabla"}):
			tds = []
			for td in tr('td'):
				tds.append(td.string)
			trs.append(tds)
		del trs[0]
		return trs

	def listMateriasPlan(self):
		return self._getInfoFromTable(self.url['materias_plan'])

	def estadoAcademico(self):
		return self._getInfoFromTable(self.url['estado_academico'])