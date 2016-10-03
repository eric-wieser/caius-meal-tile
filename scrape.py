import re
import os
from collections import namedtuple

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import ravenclient
import cache

s = requests.Session()

password = None

if not password:
	try:
		password = open(os.path.expanduser('~/password')).read()[::-1]
	except:
		pass

if not password:
	path = os.path.join(os.path.split(__file__)[0], 'ravenpassword')
	print(path)
	try:
		password = open(path).read()
	except:
		raise

if not password:
	password = input("Password (leave empty for secure prompt)")

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


def escape(s):
	return BeautifulSoup('<fix-libxml2-issue />'+s, 'html.parser').get_text()


class Menu(object):
	def __init__(self, hall):
		self.hall = hall

		self.bread = ''
		self.soup = ''
		self.starter = ''

		self.main = ''
		self.main_v = ''
		self.sides = ''

		self.dessert = ''

		self.error = None
		self.raw = ''

	def load(self, data, is_cafeteria=False):
		try:
			self._load(data, is_cafeteria)
		except Exception as e:
			raise MenuParseFailure(self.hall, data) from e

	def _load(self, data, is_cafeteria=False):
		data = re.sub(r'(\n|\r)+', ' ', data)
		lines = re.split(r'<br(?: ?\/?)>', data)
		lines = [escape(line.strip()) for line in lines]
		self.raw = '\n'.join(lines)

		if not is_cafeteria and lines[1] == '':
			lines[1] = '*'


		courses = re.split(r'\n[*_]+\n', '\n'.join(lines))
		courses = [course.strip() for course in courses]

		# remove obvious line wrapping
		courses = [
			re.sub(r'\([^)]+\)', lambda l: re.sub(r'\s+', ' ', l.group(0)), course)
			for course in courses
		]
		courses = [
			re.sub(r'(?i)\s*(\nand|and\n)\s*', ' and ', course)
			for course in courses
		]
		courses = [
			re.sub(r'(?i)\s*(\nor|or\n)\s*', ' or ', course)
			for course in courses
		]

		if len(courses) == 4:
			bread, starters, mains, dessert = courses
		elif len(courses) == 3:
			bread_and_starters, mains, dessert = courses
			bread_and_starters = bread_and_starters.split('\n', 1)
			if len(bread_and_starters) == 1:
				bread, starters = [''] + bread_and_starters
			else:
				bread, starters = bread_and_starters
		else:
			raise ValueError("Could not parse menu", (data, courses))

		starters = re.split(r'(?i)\s*\bor\b\s*', starters, 1)
		if len(starters) == 2:
			self.soup, self.starter = starters
		else:
			self.soup = ''
			self.starter = starters[0]


		self.bread = bread
		self.main, self.sides = re.split(r'\n\n+', mains, 1)
		self.dessert = dessert

		self.sides = [side.strip() for side in re.split(r'\n+', self.sides)]

		veg_courses = re.split(r'(?i)\n+Vegetarian\s*(?:[-:]\s*\n?|\n)', dessert)
		if veg_courses:
			self.dessert = veg_courses[0]
			self.main_v = re.sub(r'\s+', ' ', veg_courses[1])

		self.main = re.sub(r'\s+', ' ', self.main)


		# remove html entities
		self.bread = escape(self.bread)
		self.soup = escape(self.soup)
		self.starter = escape(self.starter)
		self.main = escape(self.main)
		self.main_v = escape(self.main_v)
		self.sides = list(map(escape, self.sides))
		self.dessert = escape(self.dessert)

		return self


class HallType(namedtuple("HallType", "id name")):
	@property
	def full_name(self):
		if 'hall' in self.name:
			return self.name
		else:
			return self.name + ' hall'


class HallError(Exception):
	pass

class MenuParseFailure(Exception):
	def __init__(self, hall, raw_menu):
		super().__init__(hall, raw_menu)
		self.hall = hall
		self.raw_menu = raw_menu

	def __str__(self):
		return "in {}\nmenu: [{}]".format(self.hall,
			self.raw_menu
				.encode('unicode_escape')
				.replace(b'<br/>', b'\n<br/>\n')
				.decode('ascii')
		)

class Hall(object):
	@cache.timed(timedelta(hours=12))
	def __new__(self, *args, **kwargs):
		return super().__new__(self)

	def __init__(self, hall_type, date):
		self.date = date
		self.type = hall_type
		self.url = urls.event(hall_type.id, date)

		self.refresh()

	def __repr__(self):
		return "Hall({!r}, {!r})".format(self.date, self.type)

	def __str__(self):
		return "'{} hall' on {:%d %b %Y} ({})".format(self.type.name, self.date, self.url)

	def __hash__(self):
		return hash((self.date, self.type))

	def __eq__(self, other):
		return (self.date, self.type) == (other.date, other.type)

	@cache.timed(timedelta(minutes=30))
	def refresh(self):
		req = s.get(self.url)
		soup = BeautifulSoup(req.text, 'html.parser')


		error_elem = soup.find(class_='error')

		if error_elem:
			raise HallError(error_elem.get_text())

		menu_elem = soup.find(class_='menu')

		if menu_elem:
			self.menu = Menu(self)
			try:
				self.menu.load(
					menu_elem.decode_contents(formatter="html"),
					is_cafeteria='cafeteria' in self.type.name
				)
			except MenuParseFailure as e:
				import traceback
				traceback.print_exc()
				self.menu.error = e
		else:
			self.menu = None

		guest_list = soup.find('table', class_='list').find_all('td', title=True)

		metadata = [
			tuple(x.get_text() for x in row.find_all('td'))
			for row in soup.find('table', class_='table').find_all('tr')
		]
		self.metadata = {
			k.rstrip(':').lower(): v
			for k, v in metadata
		}
		self.start_time = datetime.strptime(
			self.metadata['start time'], '%I:%M%p'  # ie '7:05pm'
		).time()

		self.attendees = {guest['title'] for guest in guest_list}
		self.attendee_names = {guest['title']: guest.get_text().strip() for guest in guest_list}



def normalize_hall_name(name):
	name = name.strip().lower()
	name = re.sub(r' +\(?early\)?', '', name)
	name = re.sub(r' +hall$', '', name)
	name = re.sub(r'1st', 'first', name)
	name = re.sub(r'^pre term', 'pre-term', name)
	return name

def get_hall_types():
	req = s.get(urls.root)
	soup = BeautifulSoup(req.text, 'html.parser')

	headers = soup.find_all('h2')
	header = next((h for h in headers if h.get_text() == 'Bookable events'), None)

	assert header

	table = header.find_next_sibling('table')
	a_tags = table.find_all('a')

	return [
		HallType(
			name=normalize_hall_name(a.get_text()),
			id=int(re.match(r'\?event=(\d+)', a['href']).group(1))
		)
		for a in a_tags
	]


hall_types = get_hall_types()


def halls_on(day):
	def get_halls():
		for hall_type in hall_types:
			try:
				yield Hall(hall_type, day)
			except HallError:
				pass

	return list(get_halls())




def get_user_hall(user, day):
	halls = halls_on(day)

	for hall in halls:
		if user in hall.attendees:
			return hall, True

	for hall in halls:
		if hall.menu:
			return hall, False

	if halls:
		return halls[0], False

	return None, False
