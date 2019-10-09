import re

def map(arr, func):
	try: return [func(x) for x in arr]
	except TypeError: 
		try: return [func(arr[i], i) for i in range(len(arr))]
		except TypeError: return [func(arr[i], i) for i in range(len(arr))]

def filter(arr, func):
	try: return [x for x in arr if func(x)]
	except TypeError: 
		try: return [arr[i] for i in range(len(arr)) if func(arr[i], i)]
		except TypeError: return [arr[i] for i in range(len(arr)) if func(arr[i], i)]

def reduce(arr, func, start=None):
	for i in range(0 if start==None else 1, len(arr)):
		try: start = func(arr[0] if start==None else start, arr[i])
		except TypeError:
			try: start = func(arr[0] if start==None else start, arr[i], i)
			except TypeError: start = func(arr[0] if start==None else start, arr[i], i, arr)
	return start

def has_key(key):
	def inner(obj):
		try: 
			obj[key]
			return True
		except KeyError: return False
	return inner

def get_key(key):
	def inner(obj):
		try: return obj[key]
		except KeyError: return obj
	return inner

def text_match(matcher):
	if not isinstance(matcher, str): return lambda x : False
	return lambda text : re.match(matcher, text)

def is_text_empty():
	return lambda text : not isinstance(text, str) or len(text) == 0

def is_text_not_empty():
	return lambda text : not isinstance(text, str) or len(text) > 0

def find_matches(matcher, text):
	return re.search(matcher, text)