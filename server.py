from datetime import datetime, timedelta
import itertools

from bottle import *
import scrape

host = 'efw27.user.srcf.net'
port = 8101


class bunch(object):
	def __init__(self, **kwargs):
		self.__dict__.update(**kwargs)

app = Bottle()
SimpleTemplate.defaults["domain"] = 'http://{}:{}'.format(host, port)
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


today = datetime(2014, 06, 03)

@app.route('/<user>/notification-today.xml')
@view('notification-today.xml.tpl')
def get_notifications(user):
	hall, is_booked = scrape.get_user_hall(user, today)
	if not is_booked:
		status = 'closed'
	elif 'formal' in hall.type.name:
		status = 'booked-formal'
	else:
		status = 'booked'

	return dict(
		status=status,
		hall=hall
	)

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

@app.route('/<user>/notification-nextdays.xml')
@view('notification-nextdays.xml.tpl')
def get_notifications(user):
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

app.run(host=host, port=port, debug=True)
