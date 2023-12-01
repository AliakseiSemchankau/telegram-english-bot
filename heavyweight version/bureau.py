from db import SQL

from download import download

import datetime
from constants import default_delta, today

def next_delta(delta):
	if delta == 0:
		return 24 * 3600
	if delta == 24 * 3600:
		return 3 * 24 * 3600
	return round(1.618 * delta)

def update_delta(delta, mode='D'):
	if mode == 'D':
		return next_delta(delta)
	elif mode == 'E':
		return 3 * 24 * 3600 + next_delta(delta)
	elif mode == 'M':
		return 3 * 24 * 3600
	else:
		return 1 * 24 * 3600

def generate_secret(id):
	secret = ''
	while id:
		char = chr(ord('A') + (id % 26))
		secret += char
		id = id // 26
	return secret

class Bureau:

	def __init__(self, db):
		self.SQL = SQL(db)
		self.SQL.unpend_everyone()
	
	def inscrire_user(self, chat_id):
		secret = generate_secret(chat_id)
		if self.SQL.check_chat_id(chat_id):
			return 'already registered', secret
		self.SQL.add_chat_id(chat_id, secret)
		return 'succesfully registered', secret
		
	def inscrire_user_alt(self, chat_id_alt, secret):
			record = self.SQL.select_record_for_secret(secret)
			if record is None:
				return 'secret word NOT FOUND', 'NONE'
				
			record = {
				'chat_id' : record[0], 
				'chat_id_alt' : record[1], 
				'secret': record[2]
			}
			
			self.SQL.add_chat_id_alt(chat_id_alt, secret)
			self.SQL.unpend(chat_id_alt)
			
			if record['chat_id_alt'] == chat_id_alt:
				return 'already registered', record['chat_id']	
			if record['chat_id_alt'] == 0:
				return 'succesfully registered', record['chat_id']	
			else:
				return 'succesfully overwritten previous record', record['chat_id']
				
	def inscrire_word(self, chat_id, word):
		is_in_user_list, record, is_in_db = self.SQL.check_word(chat_id, word)
		
		msg = ""
		translations, examples = download(word)
		if len(translations) > 0:
			if not is_in_db:
				self.SQL.add_translation(word, translations[0])
		else:
			return 'FAILED', [], []
			
		if not is_in_db:
			self.SQL.add_examples(word, examples)
		
		self.SQL.add_word(chat_id, word, today(), default_delta)
	
		expl = translations[0]
		demos = examples[:min(2, len(examples))]

		if not is_in_user_list:
			return 'added', expl, demos
		else:
			return 'renewed', expl, demos
			
	def update_queue(self, chat_id, record, verdict, mode='D'):
		delta = default_delta if (verdict == 'I' and mode == 'D') else update_delta(record['delta'], mode=mode)
		self.SQL.add_word(chat_id, record['word'], today(), delta)
		return delta
		
	def pend(self, chat_id_alt):
		self.SQL.pend(chat_id_alt)
	
	def unpend(self, chat_id_alt):
		self.SQL.unpend(chat_id_alt)
		
	def remove_user_alt(self, chat_id_alt):
		self.SQL.remove(chat_id_alt)
		
	def remove_word(self, chat_id, word):
		self.SQL.remove_word(chat_id, word)
