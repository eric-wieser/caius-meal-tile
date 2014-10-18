from datetime import date, timedelta
import itertools
from datetime import date, datetime, timedelta
from collections import namedtuple

from bottle import *

import scrape


# utils for scraping
class bunch(object):
	def __init__(self, **kwargs):
		self.__dict__.update(**kwargs)

def get_day_book_status(user, start_date):
	for i in range(100):
		res = bunch(
			date=start_date + timedelta(days=i),
			hall=None
		)

		hall, is_booked = scrape.get_user_hall(user, res.date)
		if is_booked:
			res.hall = hall
		if hall:
			yield res

def get_user_halls_from(user, start_date):
	for i in range(100):
		date = start_date + timedelta(days=i)

		hall, is_booked = scrape.get_user_hall(user, date)
		if hall:
			yield hall, is_booked

		print "Failed {}".format(i)



app = Bottle()
SimpleTemplate.defaults["get_url"] = app.get_url

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
	if request.forms.calendar:
		_, host, _, _, _ = request.urlparts
		return redirect('webcal://{}/{}.ics'.format(host, request.forms.crsid))
	elif request.forms.vegetarian:
		return redirect('/' + request.forms.crsid + '-v')
	else:
		return redirect('/' + request.forms.crsid)


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

	print repr(hall)

	return dict(
		status=status,
		hall=hall,
		user=user.crsid,
		vegetarian=user.vegetarian
	)

@app.route('/<user:user>/browserconfig.xml')
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

	print repr(hall)

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
		days=list(itertools.islice(get_day_book_status(user.crsid, today), 5))
	)

if __name__ == '__main__':
	host = 'efw27.user.srcf.net'
	port = 8101
	SimpleTemplate.defaults["domain"] = 'http://{}:{}'.format(host, port)
	app.run(host=host, port=port, debug=True)
else:
	import bottle
	bottle.debug(True)
	SimpleTemplate.defaults["domain"] = 'http://meal-tile.efw27.user.srcf.net:8989'
