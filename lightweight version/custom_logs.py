import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import bcolors as bf

mode_to_color = {
	'E': bf.OKGREEN,
	'M': bf.OKBLUE,
	'H': bf.WARNING,
	'R': bf.FAIL
}

def log_exception(ex, func_name, args):
	template = "An exception of type {0} occurred. Arguments:\n{1}"
	message = template.format(type(ex).__name__, args)
	print(f'{bf.FAIL}[{func_name}]{bf.ENDC}: ' + message)
	e = str(ex)
	if len(e) < 200:
		print(f'{bf.FAIL}[actual exception]{bf.ENDC}: ' + e)

def log_json(word, y):
	print(f'{bf.CBEIGE}[download_word]{bf.ENDC}: word={bf.OKGREEN}{word}{bf.ENDC}')
	for key in sorted(y, reverse=True):
		val = y[key]
		if isinstance(val, str):
			print(f'      {bf.OKBLUE}{key}{bf.ENDC}: {val}')
		elif isinstance(val, list):
			print(f'      {bf.OKBLUE}{key}{bf.ENDC}:')
			for v in val:
				print(f'                {bf.WARNING}{v}{bf.ENDC}')

def log_add_word(chat_id, is_russian, word, result):
	print(f'{bf.OKCYAN}[add_word]{bf.ENDC}: chat_id={chat_id}, is_russian={is_russian}, word=' + f'{bf.OKGREEN}' + str(word) + f'{bf.ENDC}' + f', len(result)={len(result)}')
