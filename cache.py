from datetime import datetime
from collections import namedtuple
import functools
import sys

def timed(delta):
	"""
	like @lru_cache, but recalculates values after they have expired
	"""
	def decorator(f):
		data = {}

		def _serialize(*args, **kwargs):
			try:
				exc = None
				res = f(*args, **kwargs)
			except Exception as e:
				res = None
				exc = e
			return timed.Entry(at=datetime.now(), value=res, exc=exc)

		def _deserialize(entry):
			if entry.exc is not None:
				raise entry.exc.with_traceback(entry.exc.__traceback__.tb_next)
			else:
				return entry.value

		@functools.wraps(f)
		def wrapped(*args, **kwargs):
			arg_key = (args, tuple(kwargs.items()))
			d = data.get(arg_key)
			if not d:
				d = data[arg_key] = _serialize(*args, **kwargs)
			elif datetime.now() - d.at >= delta:
				d = data[arg_key] = _serialize(*args, **kwargs)
			return _deserialize(d)

		return wrapped
	return decorator

timed.Entry = namedtuple('Entry', 'at value exc')

if __name__ == '__main__':
	import unittest
	from datetime import timedelta
	import time
	import traceback

	class TestCache(unittest.TestCase):
		def test_simple(self):
			called = 0
			@timed(timedelta(seconds=0.1))
			def square(x):
				nonlocal called
				called += 1
				return x * x

			self.assertEqual(square(2), 4)
			self.assertEqual(called, 1)
			self.assertEqual(square(3), 9)
			self.assertEqual(called, 2)
			self.assertEqual(square(2), 4)
			self.assertEqual(called, 2)
			time.sleep(0.15)
			self.assertEqual(square(2), 4)
			self.assertEqual(called, 3)

		def test_exception(self):
			@timed(timedelta(seconds=0.1))
			def throw(x):
				raise x
			try:
				throw(ValueError())
			except ValueError:
				print('> ' + traceback.format_exc().replace('\n', '\n> '))
			try:
				throw(ValueError())
			except ValueError:
				print('> ' + traceback.format_exc().replace('\n', '\n> '))

	unittest.main()