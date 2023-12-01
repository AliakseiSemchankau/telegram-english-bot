import subprocess
from pprint import pprint

import re
import json

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import SCRIPT

import openai
from secret_tokens import OPEN_AI_TOKEN
openai.api_key = OPEN_AI_TOKEN

from custom_logs import log_json, log_exception

def open_words(words):
	word = words[0]
	msg = f'''
		For a context, you are an English teacher.
		Please provide a couple of usage examples for the following word: {word}. 
		Then insert an empty line and give brief explanation for the word: {word}'
		'''
	print('msg = ', msg)
	completion = openai.ChatCompletion.create(
  		model="gpt-3.5-turbo",
  		messages=[{"role": "user", "content": msg}],
  		temperature=0.8
	)

	j = completion.choices[0].message.content

	with open('completion.txt', 'a') as file:
		file.write('\n\n\n' + j)

	return j

def open_word(word):

	msg = f'''
		Please give a concise definition of the word {word} and give usage examples. Also give synonyms to the word {word} with explanations'
		'''

	completion = openai.ChatCompletion.create(
  		model="gpt-3.5-turbo",
  		messages=[{"role": "user", "content": msg}],
  		temperature=0.5
	)

	j = completion.choices[0].message.content

	with open('completion.txt', 'a') as file:
		file.write('\n\n\n' + j)

	return j

def open_russian_word(word):

	msg = f'''
		Please translate Russian word {word} to English. Give all the possible translations, explain how they are different from each other, and give usage examples.'
		'''

	completion = openai.ChatCompletion.create(
  		model="gpt-3.5-turbo",
  		messages=[{"role": "user", "content": msg}],
  		temperature=0.5
	)

	j = completion.choices[0].message.content

	with open('completion.txt', 'a') as file:
		file.write('\n\n\n' + j)

	return j
	
def download(word):
	try:
		result = open_word(word)
		return result
	except Exception as e:
		log_exception(e, "download:1")
	return None

def download_russian(word):
	try:
		result = open_russian_word(word)
		return result
	except Exception as e:
		log_exception(e, "download:1")
	return None

def paragraph(words):
	try:
		result = open_words(words)
		return result
	except Exception as e:
		log_exception(e, "download:1")
	return None
		

	

	

