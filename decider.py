from db import SQL

from download import download

import datetime
import random
from pprint import pprint

import datetime
from constants import default_date, default_delta

def choose_one(array):
	if len(array) == 0:
		return None
	return array[random.randint(0, len(array) - 1)]

def update_delta(delta):
	if delta == 24 * 3600:
		return 3 * 24 * 3600
	return round(1.618 * delta)

def generate_secret(id):
	secret = ''
	while id:
		char = chr(ord('A') + (id % 26))
		secret += char
		id = id // 26
	return secret	

def today():
	return (datetime.datetime.utcnow() - default_date).seconds

class Decider:


	def __init__(self, db):
		self.SQL = SQL(db)
		self.SQL.unpend_everyone()
	
	def register_user(self, chat_id):
		secret = generate_secret(chat_id)
		if self.SQL.check_chat_id(chat_id):
			return 'already registered', secret
		self.SQL.add_chat_id(chat_id, secret)
		return 'succesfully registered', secret
		
	def register_user_alt(self, chat_id_alt, secret):
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

	def get_chat_id(self, chat_id_alt):
		return self.SQL.select_chat_id(chat_id_alt)
		
	def get_chat_id_alts(self):
		return self.SQL.select_chat_id_alts()

	def register_word(self, chat_id, word):
		is_in_user_list, record, is_in_db = self.SQL.check_word(chat_id, word)
		
		msg = ""
		translations, examples = download(word)
		if len(translations) > 0:
			if not is_in_db:
				self.SQL.add_translation(word, translations[0])
			msg +=  '\n\n' + translations[0]
		else:
			return 'FAILED', ''
			
		if not is_in_db:
			self.SQL.add_examples(word, examples)
		msg += '\n\n' + '\n'.join(examples)
		
		self.SQL.add_word(chat_id, word, today(), default_delta)
	
		if not is_in_user_list:
			return 'added', msg
		else:
			return 'renewed', msg

	def get_full_word_record(self, record):
		word = record['word']
		full_record = {
			'chat_id'     : record['chat_id'], 
			'delta'       : record['delta'],
			'last'        : record['last'],
			'word'        : word,
			'translation' : self.SQL.select_translation(word),
			'example'     : choose_one(self.SQL.select_examples(word))
		}
		return full_record

	def get_word_for_id(self, chat_id):
		records = [{'chat_id' : chat_id, 'word' : r[0], 'last' : r[1], 'delta' : r[2]} for r in self.SQL.select_records(chat_id)]
		records = [r for r in records if r['last'] + r['delta'] <= today()]
		if len(records) == 0:
			return None
		r = choose_one(records)
		full_record = self.get_full_word_record(r)
		return full_record

	def update_queue(self, chat_id, record, verdict):
		delta = default_delta if verdict == 'INCORRECT' else update_delta(record['delta'])
		self.SQL.add_word(chat_id, record['word'], today(), delta)
		return delta
	
	def is_pending(self, chat_id_alt):
		return self.SQL.check_pending(chat_id_alt)	
		
	def pend(self, chat_id_alt):
		self.SQL.pend(chat_id_alt)
	
	def unpend(self, chat_id_alt):
		self.SQL.unpend(chat_id_alt)
		
	def remove(self, chat_id_alt):
		self.SQL.remove(chat_id_alt)

		
