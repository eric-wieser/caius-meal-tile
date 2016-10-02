import itertools
import re
from datetime import date, datetime, timedelta
from collections import namedtuple

import icalendar
import pytz
from bottle import *

import scrape

timezone = pytz.timezone("Europe/London")

# utils for scraping
class bunch(object):
	def __init__(self, **kwargs):
		self.__dict__.update(**kwargs)

def get_day_book_status(user, start_date):
	for i in range(30):
		res = bunch(
			date=start_date + timedelta(days=i),
			hall=None,
			is_booked=False
		)

		res.hall, res.is_booked = scrape.get_user_hall(user, res.date)

		yield res

def get_user_halls_from(user, start_date):
	for i in range(30):
		date = start_date + timedelta(days=i)

		hall, is_booked = scrape.get_user_hall(user, date)
		if hall:
			yield hall, is_booked

		print("Failed {}".format(i))



app = Bottle()
SimpleTemplate.defaults["get_url"] = app.get_url

def get_abs_url(*args, **kwargs):
	parts = request.urlparts
	path = app.get_url(*args, **kwargs)
	return parts._replace(path=path).geturl()

SimpleTemplate.defaults["get_abs_url"] = get_abs_url



# url routing helper
User = namedtuple('User', 'crsid vegetarian')
def user_filter(config):
    regexp = r'[a-z]+[0-9]*(-v)?'

    def to_python(match):
        return User(match[:-2], True) if match.endswith('-v') else User(match, False)

    def to_url(user):
        return user.crsid + ('-v' if user.vegetarian else '')

    return regexp, to_python, to_url

app.router.add_filter('user', user_filter)


@app.route('/images/<path:path>', name='images')
def images(path):
	return static_file(path, root='images')

@app.route('/')
def base():
	return static_file('index.html', root='.')

@app.post('/')
def submit():
	user = User(request.forms.crsid, bool(request.forms.vegetarian))

	if request.forms.calendar:
		url = request.urlparts._replace(
			scheme='webcal',
			path=request.urlparts.path + '{}.ics'.format(user.crsid)
		).geturl()
		calendar_file(user)  # prebuild calendar
		print("Calendar built for {}".format(user))
		return redirect(url)
	else:
		return redirect(app.get_url('user-page', user=user))


@app.route('/<user:user>', name="user-page")
@app.route('/<user:user>/')
@view('user.tpl')
def user_page(user):
	today = date.today()
	hall, is_booked = next(get_user_halls_from(user.crsid, today))
	if not is_booked:
		status = 'closed'
	elif 'formal' in hall.type.name:
		status = 'booked-formal'
	else:
		status = 'booked'

	print(repr(hall))

	return dict(
		status=status,
		hall=hall,
		user=user,
		vegetarian=user.vegetarian
	)

@app.route('/<user:user>/browserconfig.xml', name='browserconfig')
@view('browserconfig.xml.tpl')
def browserconfig(user):
	return dict(user=user)

@app.route('/<user:user>/notification-today.xml', name='nt-today')
@view('notification-today.xml.tpl')
def notifications_today(user):
	today = date.today()
	hall, is_booked = next(get_user_halls_from(user.crsid, today))
	if not is_booked:
		status = 'closed'
	elif 'formal' in hall.type.name:
		status = 'booked-formal'
	else:
		status = 'booked'

	print(repr(hall))

	return dict(
		status=status,
		hall=hall,
		vegetarian=user.vegetarian
	)


@app.route('/<user:user>/notification-nextdays.xml', name='nt-nextdays')
@view('notification-nextdays.xml.tpl')
def notifications_nextdays(user):
	today = date.today()
	hall, is_booked = scrape.get_user_hall(user.crsid, today)
	if not is_booked:
		status = 'closed'
	elif 'formal' in hall.type.name:
		status = 'booked-formal'
	else:
		status = 'booked'

	return dict(
		status=status,
		days=list(itertools.islice((s for s in get_day_book_status(user.crsid, today) if s.hall), 5))
	)

@app.route('/<user:user>.ics')
def calendar_file(user):
	start_date = date.today() - timedelta(days=7)

	cal = icalendar.Calendar()
	cal['prodid'] = '-//Eric Wieser//Caius Meal Tile//EN'
	cal['version'] = '2.0'
	cal['x-wr-calname'] = 'Caius Hall' + ' ({})'.format(request.query.extra) if request.query.extra else ''
	cal['x-wr-caldesc'] = 'Hall bookings'

	bookings = itertools.islice(get_day_book_status(user.crsid, start_date), 7*3)

	for booking in bookings:
		hall = booking.hall
		if booking.is_booked:
			# get the start time in UTC
			start_dt = datetime.combine(hall.date, hall.start_time)
			start_dt = timezone.localize(start_dt).astimezone(pytz.utc)

			event = icalendar.Event()
			event['summary'] = icalendar.vText(hall.type.full_name.capitalize())
			event['dtstart'] = icalendar.vDatetime(start_dt)
			event['dtend'] = icalendar.vDatetime(start_dt + timedelta(minutes=50))
			event['dtstamp'] = icalendar.vDatetime(datetime.now())
			event['description'] = icalendar.vText(hall.menu.raw if hall.menu else 'No menu')
			event['location'] = icalendar.vText(', '.join([
				"Gonville & Caius: Old Courts",
				"Trinity St",
				"Cambridge",
				"CB2 1TA"
			]))
			event['uid'] = icalendar.vText(
				'{}.{}.meal-tile@efw27.user.srcf.net'.format(
					re.sub(r'\W+', '-', hall.type.name),
					hall.date.isoformat()
				)
			)

			for crsid in sorted(hall.attendees):
				attendee = icalendar.vCalAddress('MAILTO:{}@cam.ac.uk'.format(crsid))
				attendee.params['cn'] = icalendar.vText(hall.attendee_names[crsid])
				attendee.params['role'] = icalendar.vText('REQ-PARTICIPANT')
				attendee.params['partstat'] = icalendar.vText('ACCEPTED')
				attendee.params['cutype'] = icalendar.vText('INDIVIDUAL')

				event.add('attendee', attendee, encode=0)

			cal.add_component(event)

	response.content_type = 'text/calendar; charset=UTF-8'
	return cal.to_ical()

# HACK!
app.mount('/meal-tile', app)

if __name__ == '__main__':
	host = 'efw27.user.srcf.net'
	port = 8101
	app.run(host=host, port=port, debug=True)
else:
	import bottle
	bottle.debug(True)
