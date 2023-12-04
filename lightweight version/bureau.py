import datetime

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import default_delta, today

from db import SQL

from download import download

class Bureau:

	def __init__(self, db):
		self.SQL = SQL(db)

	def inscrire_user(self, chat_id):
		if self.SQL.check_chat_id(chat_id):
			return 'already registered'
		self.SQL.add_chat_id(chat_id)
		return 'succesfully registered'

	def inscrire_word(self, chat_id, word):	
		self.SQL.add_word(chat_id, word, today(), default_delta)
			
	def remove_word(self, chat_id, word):
		self.SQL.remove_word(chat_id, word)
			