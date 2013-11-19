 # -*- coding: utf-8 -*-
import requests
from BeautifulSoup import BeautifulSoup
from conf import *

class SysacadSession:
	"Sesión de SysCAD."

	url = URLS_DICT

	def __init__(self, fr):
		self.base_url = BASE_URL[fr]

	def _get(self, url_action):
		if not 'cookies' in dir(self):
			raise Exception('Debes primero hacer login.')
		url = self.base_url + url_action
		return requests.get(url, cookies=self.cookies) 

	def _post(self, url_action, data):
		if not 'cookies' in dir(self):
			raise Exception('Debes primero hacer login.')
		url = self.base_url + url_action
		return requests.post(url, cookies=self.cookies, data=data)

	def login(self, legajo, password):

		# Make request
		url = self.base_url + self.url['login']
		response = requests.post(url, data={'legajo': legajo,'password': password})

		# Handle incorrect login
		html = BeautifulSoup(response.text)
		if html.title.string == u'Ingreso Alumnos al SYSACAD' or html('p', attrs={'class': "textoError"}):
			raise Exception('Información de login incorrecta.')

		# Store session cookie
		for key in response.cookies.keys():
			if key.find(SESSION_COOKIE_NAME):
				break
		self.cookies = {key: response.cookies[key]}

	def _getInfoFromTable(self, url, keys):
		response = self._get(url)
		html = BeautifulSoup(response.text)
		data = []
		for tr in html('tr', attrs={'class': "textoTabla"}):
			tds = {}
			i = 0
			for td in tr('td'):
				tds[keys[i]] = td.getText()
				i += 1
			data.append(tds)
		del data[0]
		return data

	def listMateriasPlan(self):
		keys = ('anio', 'duracion', 'nombre', 'se_cursa', 'se_rinde')
		return self._getInfoFromTable(self.url['materias_plan'], keys)

	def estadoAcademico(self):
		keys = ('anio', 'nombre', 'estado', 'plan')
		return self._getInfoFromTable(self.url['estado_academico'], keys)

	def correlatividadCursado(self):
		keys = ('anio', 'nombre', 'estado', 'plan')
		return self._getInfoFromTable(self.url['correlatividad_cursado'], keys)
