from db import SQL

import random

from constants import today

def obliterate_sentence(e, word):
	if e is None:
		return None
	def f(v):
		x = set(word.upper())
		y = set(v.upper())
		return len(x.intersection(y))**2 / ((len(x) + 1.0) * (len(y) + 1.0)) 
		
	def g(v):
		if f(v) < 0.5:
			return v
		return (len(v) // 2) * '_'
		
	e = ' '.join([g(v) for v in e.split(' ')])
	return e

def choose_one(array):
	if len(array) == 0:
		return None
	return array[random.randint(0, len(array) - 1)]

class Decider:

	def __init__(self, db):
		self.SQL = SQL(db)
		self.SQL.unpend_everyone()

	def get_chat_id(self, chat_id_alt):
		return self.SQL.select_chat_id(chat_id_alt)
		
	def get_chat_id_alts(self):
		return self.SQL.select_chat_id_alts()

	def get_full_word_record(self, record):
		word = record['word']
		full_record = {
			'chat_id'     : record['chat_id'], 
			'delta'       : record['delta'],
			'last'        : record['last'],
			'word'        : word,
			'translation' : obliterate_sentence(self.SQL.select_translation(word), word),
			'example'     : obliterate_sentence(choose_one(self.SQL.select_examples(word)), word)
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
	
	def is_pending(self, chat_id_alt):
		return self.SQL.check_pending(chat_id_alt)	

		
