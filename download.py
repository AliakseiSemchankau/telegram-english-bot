import subprocess

from pprint import pprint

from secrets import SCRIPT

def process_example(word, e):
	def f(v):
		x = set(word.upper())
		y = set(v.upper())
		return -len(x.intersection(y))**2 / ((len(x) + 1.0) * (len(y) + 1.0)) 
	
		
	def g(goat, v):
		if v != goat:
			return v
		return (len(goat) // 2) * '_'
		
	words = sorted(e.split(' '), key = lambda w : f(w))
	goat = words[0]
	if f(goat) > -0.5:
		return ''
	e = ' '.join([g(goat, v) for v in e.split(' ')])
	return e

def download(word):
	try:
		results = subprocess.run([SCRIPT, word], stdout=subprocess.PIPE, timeout=3).stdout.decode('utf-8')
		print(results)
	except Exception as e:
		return [], []
	if "you've entered isn't in the" in results:
		return [], []
	results = results.split('\n')
	results = [r.replace('\x1b[0m', '') for r in results]
	results = [r for r in results if 'Cambridge Advanced' not in r]
	results = [r for r in results if '"' not in r]
	
	translations = [r.replace('\x1b[34m', '').strip() for r in results if '\x1b[34m' in r]
	examples = [r.replace('\x1b[38;2;117;117;117m', '').strip() for r in results  if '\x1b[38;2;117;117;117m' in r]
	
	# examples = [e for e in examples if '"' not in e]
	examples = [process_example(word, e) for e in examples]
	examples = [e for e in examples if len(e) > 3]

	return translations, examples

