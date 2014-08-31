from datetime import datetime
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

@app.route('/<user>/notification.xml')
@view('notifications.xml.tpl')
def get_notifications(user):
	hall, is_booked = scrape.get_user_hall(user)
	return dict(
		status='booked' if is_booked else 'closed',
		hall=hall
	)

app.run(host=host, port=port, debug=True)
