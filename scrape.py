import re
import os

import requests
from bs4 import BeautifulSoup
from datetime import datetime

import ravenclient

s = requests.Session()

password = None

if not password:
	try:
		password = open(os.path.expanduser('~/password')).read()[::-1]
	except:
		pass

if not password:
	password = raw_input("Password (leave empty for secure prompt)")

if not password:
	import getpass
	password = getpass.getpass()


s.mount(ravenclient.auth_url, ravenclient.HTTPAdapter('efw27', password))

class urls(object):
	root = 'https://www.mealbookings.cai.cam.ac.uk'

	@classmethod
	def hall(cls, hall_id):
		return '{}/index.php?event={}'.format(cls.root, hall_id)

	@classmethod
	def event(cls, hall_id, day):
		return '{}/index.php?event={}&date={:%Y-%m-%d}'.format(cls.root, hall_id, day)


class Menu(object):
	def __init__(self):
		self.bread = ''
		self.soup = ''
		self.starter = ''

		self.main = ''
		self.main_v = ''
		self.sides = ''

		self.dessert = ''

	def load(self, data, is_cafeteria=False):
		data = re.sub(r'\n', ' ', data)
		lines = re.split(r'<br(?: ?\/?)>', data)
		lines = [line.strip() for line in lines]

		if not is_cafeteria and lines[1] == '':
			lines[1] = '*'


		courses = '\n'.join(lines).split('\n*\n')
		courses = [course.strip() for course in courses]

		# remove obvious line wrapping
		courses = [
			re.sub(r'\([^)]+\)', lambda l: re.sub('\s+', ' ', l), course)
			for course in courses
		]

		if len(courses) == 4:
			bread, starters, mains, dessert = courses
		elif len(courses) == 3:
			bread_and_starters, mains, dessert = courses
			bread, starters = bread_and_starters.split('\n', 1)

		starters = re.split(r'\s*or\s*', starters, 1)
		if len(starters) == 2:
			self.soup, self.starter = starters
		else:
			self.soup = ''
			self.starter = starters


		self.bread = bread
		self.main, self.sides = re.split(r'\n\n+', mains, 1)
		self.dessert = dessert

		veg_courses = re.split(r'\n+Vegetarian\s*(?:-\s*\n?|\n)', dessert)
		if veg_courses:
			self.dessert = veg_courses[0]
			self.main_v = re.sub(r'\s+', ' ', veg_courses[1])

		self.main = re.sub(r'\s+', ' ', self.main)

		return self

class Hall(object):
	def __init__(self, hall_id, date):
		self.date = date
		self.type_id = hall_id

		req = s.get(urls.event(hall_id, today))
		soup = BeautifulSoup(req.text)

		menu_elem = soup.find(class_='menu')

		if menu_elem:
			self.menu = Menu().load(menu_elem.decode_contents(formatter="html"))
		else:
			self.menu = None

		guest_list = soup.find('table', class_='list').find_all('td', title=True)

		self.attendees = {guest['title'] for guest in guest_list}



def get_hall_ids():
	req = s.get(urls.root)
	soup = BeautifulSoup(req.text)

	header = soup.find('h2')

	assert header.get_text() == 'Bookable events'

	table = header.find_next_sibling('table')
	a_tags = table.find_all('a')

	return [
		re.match(r'\?event=(\d+)', a['href']).group(1)
		for a in a_tags
	]


hall_ids = [323] + get_hall_ids()
today = datetime(2014, 06, 03)


def get_user_hall(user):
	halls = [
		Hall(hall_id, today)
		for hall_id in hall_ids
	]
	for hall in halls:
		if user in hall.attendees:
			return hall, True

	for hall in halls:
		if hall.menu:
			return hall, False

	return None, False
