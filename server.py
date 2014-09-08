from datetime import date, timedelta
import itertools

from bottle import *
import scrape


class bunch(object):
	def __init__(self, **kwargs):
		self.__dict__.update(**kwargs)

app = Bottle()

SimpleTemplate.defaults["get_url"] = app.get_url


@app.route('/images/<path:path>', name='images')
def images(path):
	return static_file(path, root='images')

@app.route('/')
def base():
	return static_file('index.html', root='.')

@app.route('/<user>')
@app.route('/<user>/')
@view('user.tpl')
def images(user):
	return dict(user=user)

@app.route('/<user>/browserconfig.xml')
@view('browserconfig.xml.tpl')
def images(user):
	return dict(user=user)


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

@app.route('/<user>/notification-today.xml')
@view('notification-today.xml.tpl')
def get_notifications(user):
	today = date.today()
	hall, is_booked = next(get_user_halls_from(user, today))
	if not is_booked:
		status = 'closed'
	elif 'formal' in hall.type.name:
		status = 'booked-formal'
	else:
		status = 'booked'

	print repr(hall)

	return dict(
		status=status,
		hall=hall
	)


@app.route('/<user>/notification-nextdays.xml')
@view('notification-nextdays.xml.tpl')
def get_notifications(user):
	today = date.today()
	hall, is_booked = scrape.get_user_hall(user, today)
	if not is_booked:
		status = 'closed'
	elif 'formal' in hall.type.name:
		status = 'booked-formal'
	else:
		status = 'booked'

	return dict(
		status=status,
		days=list(itertools.islice(get_day_book_status(user, today), 5))
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

