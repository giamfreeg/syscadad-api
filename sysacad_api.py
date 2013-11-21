 # -*- coding: utf-8 -*-
import requests, re
from BeautifulSoup import BeautifulSoup
from conf import *

class SysacadSession:
	"Sesión de SysCAD."

	url = URLS_DICT

	def __init__(self, base_url=None, cookies=None):
		self.base_url = base_url or DEFAULT_BASE_URL
		self.cookies = cookies

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

	def datosAlumno(self):
		response = self._get(self.url['estado_academico'])
		html = BeautifulSoup(response.text)
		cadena = html('td', attrs={'class': "tituloTabla"})[0].getText()
		p = re.compile(ur'Estado académico de (.*), (.*) al .* PM')
		data = p.search(cadena).groups()
		return {'nombre': data[1], 'apellido': data[0]}

	def materiasEnCurso(self):
		estado_academico = self.estadoAcademico()
		materias = []
		for materia in estado_academico:
			if materia['estado'].find('Cursa') != -1:
				materias.append(materia['nombre'])
		return materias

	def allDataFromEstadoAcademico(self):
		# Inicializar
		data = {}
		response = self._get(self.url['estado_academico'])
		html = BeautifulSoup(response.text)

		# Datos alumno
		cadena = html('td', attrs={'class': "tituloTabla"})[0].getText()
		p = re.compile(ur'Estado académico de (.*), (.*) al .* PM')
		groups = p.search(cadena).groups()
		data['nombre_alumno'] = groups[0]
		data['apellido_alumno'] = groups[1]

		#Datos de la materia
		data['materias'] = []
		keys = ('anio', 'nombre', 'estado', 'plan')
		materias = []
		for tr in html('tr', attrs={'class': "textoTabla"}):
			tds = {}
			i = 0
			for td in tr('td'):
				tds[keys[i]] = td.getText()
				i += 1
			materias.append(tds)
		del materias[0]
		aprobadas_regex = re.compile(ur'Aprobada con (\d*) Tomo: (\d*) Folio: (\d*)')
		cursa_regex = re.compile(ur'Cursa en (.*) Aula (.*)')
		regular_regex = re.compile(ur'Regularizada en (\d*)( \(.*\))?')
		for mat in materias:
			materia = {}
			materia['anio'] = mat['anio']
			materia['nombre'] = mat['nombre']
			materia['plan'] = mat['plan']

			match = aprobadas_regex.search(mat['estado'])
			if match != None:
				groups = match.groups()
				materia['estado'] = {
					'estado': 'aprobada',
					'nota': groups[0],
					'tomo': groups[1],
					'folio': groups[2],
				}
				data['materias'].append(materia)
				continue

			match = cursa_regex.search(mat['estado'])
			if match != None:
				groups = match.groups()
				materia['estado'] = {
					'estado': 'cursa',
					'comision': groups[0],
					'aula': groups[1],
				}
				data['materias'].append(materia)
				continue

			match = regular_regex.search(mat['estado'])
			if match != None:
				groups = match.groups()
				materia['estado'] = {
					'estado': 'regular',
					'anio': groups[0],
				}
				data['materias'].append(materia)
				continue

			materia['estado'] = {'estado': 'no_inscripto'}
			data['materias'].append(materia)
		return data