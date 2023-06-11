import subprocess
from pprint import pprint

from constants import SCRIPT

import openai
from secrets import OPEN_AI_TOKEN
openai.api_key = OPEN_AI_TOKEN

import re
import json

def contains(e, word):
	def f(v):
		x = set(word.upper())
		y = set(v.upper())
		return len(x.intersection(y))**2 / ((len(x) + 1.0) * (len(y) + 1.0)) 
		
	for v in e.split(' '):
		if f(v) > 0.5:
			return True
	return False	


def download_camb(word):
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
	examples = [e for e in examples if contains(e, word)]
	examples = [e for e in examples if len(e) > 3]

	return translations, examples
	
def download_open(word):

	msg = f'''
		Forget previous instructions.
		Give me explanation for the word {word} and provide two usage examples. 
		Better be lengthy than short. 
		Return the JSON which has fields "explanation" and "examples". 
		All the information regarding the word should be in one of these fields. 
		Return JSON only.
		'''

	completion = openai.ChatCompletion.create(
  		model="gpt-3.5-turbo",
  		messages=[{"role": "user", "content": msg}],
  		temperature=0.5
	)

	j = completion.choices[0].message.content
	j = max(re.findall(r'{[^{}]+}', j), key = len)
	y = json.loads(j)
	pprint(y)
	
	translations = [y['explanation']]
	examples = ['• ' + e for e in y['examples']]
	
	return translations, examples
	
def download(word):
	translations, examples = [], []
	try:
		translations, examples = download_open(word)
	except Exception as e:
		print(e)
	if len(translations):
		return translations, examples
	try:
		translations, examples = download_camb(word)
	except Exception as e:
		print(e)
	if len(translations):
		return translations, examples
	return [], []
		

	

	

