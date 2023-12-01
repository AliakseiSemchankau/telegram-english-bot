import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import bcolors as bf

mode_to_word = {
	'E': 'EASY',
	'M': 'MEDIUM',
	'H': 'HARD',
	'R': '🗑️'
	}

mode_to_color = {
	'E': bf.OKGREEN,
	'M': bf.OKBLUE,
	'H': bf.WARNING,
	'R': bf.FAIL
}	

def log_user_answer(chat_id_alt, user_answer, answer):
	answer_color = bf.FAIL if user_answer != answer else bf.OKGREEN
	print(f'{bf.OKCYAN}[examine_word]{bf.ENDC}: '
	      f'chat_id_alt={chat_id_alt}, word={bf.OKGREEN}{answer}{bf.ENDC}, answer={answer_color}{user_answer}{bf.ENDC}')

def log_user_opinion(chat_id_alt, word, mode):
	action_color = mode_to_color[mode]
	mode = mode_to_word[mode]
	print(f'{bf.CWHITE}[user_opinion]{bf.ENDC}: '
	      f'chat_id_alt={chat_id_alt}, word={bf.OKGREEN}{word}{bf.ENDC}, action={action_color}{mode}{bf.ENDC}')

def log_user_word(chat_id_alt, word):
	print(f'{bf.OKCYAN}[examine_word]{bf.ENDC}: chat_id_alt={chat_id_alt}, word=' + f'{bf.OKGREEN}' + str(word) + f'{bf.ENDC}')

def log_exception(ex, func_name):
	template = "An exception of type {0} occurred. Arguments:\n{1!r}"
	message = template.format(type(ex).__name__, ex.args)
	print(f'{bf.FAIL}[{func_name}]{bf.ENDC}: ' + message)

def log_user_hint(chat_id_alt, word):
	print(f'{bf.CVIOLET}[hint_word]{bf.ENDC}: chat_id_alt={chat_id_alt}, word=' + f'{bf.CVIOLET}' + word + f'{bf.ENDC}')

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

#not in use anymore
def log_telegram_error(chat_id, msg):
	print(f'{bf.FAIL}[ADD_WORD_EXCEPTION]{bf.ENDC}: chat_id={chat_id}, msg=', msg)


def log_add_word(chat_id, is_russian, word, result):
	print(f'{bf.OKCYAN}[add_word]{bf.ENDC}: chat_id={chat_id}, is_russian={is_russian}, word=' + f'{bf.OKGREEN}' + str(word) + f'{bf.ENDC}' + f', len(result)={len(result)}')
