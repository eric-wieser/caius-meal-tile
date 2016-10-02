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
			except Exception:
				res = None
				exc = sys.exc_info()
			return timed.Entry(at=datetime.now(), value=res, exc=exc)

		def _deserialize(entry):
			if entry.exc is not None:
				raise entry.exc[0](entry.exc[1]).with_traceback(entry.exc[2])
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
