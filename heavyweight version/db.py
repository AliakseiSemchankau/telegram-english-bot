import sqlite3

import os

from pprint import pprint

from constants import bcolors as bf

class SQL:

	def create(self, db):
		conn = sqlite3.connect(db)
		print("Opened database successfully")
		with conn:
			conn.execute('''CREATE TABLE users
					(CHAT_ID       INT PRIMARY KEY    NOT NULL,
					 CHAT_ID_ALT   INT                NOT NULL,
					 SECRET        TEXT               NOT NULL);''')

			conn.execute('''CREATE TABLE user_words
					(CHAT_ID       INT                NOT NULL,
					WORD           TEXT               NOT NULL,
					LAST           INT                NOT NULL,
					DELTA          INT                NOT NULL,
					CONSTRAINT uw UNIQUE(CHAT_ID, WORD));''')

			conn.execute('''CREATE TABLE word_translation
					(WORD          TEXT PRIMARY KEY   NOT NULL,
					TRANSLATION    TEXT               NOT NULL);''')
         			
			conn.execute('''CREATE TABLE word_examples
					(WORD          TEXT               NOT NULL,
					EXAMPLE        TEXT               NOT NULL);''')
					
			conn.execute('''CREATE TABLE user_pending
					(CHAT_ID_ALT   INT PRIMARY KEY    NOT NULL,
					IS_PENDING     INT                NOT NULL);''')

		print("Table created successfully")

	def __init__(self, db):
		self.db = db
		if not os.path.isfile(db):
			self.create(db)
		
	def execute_query(self, query):
		try:
			conn = sqlite3.connect(self.db)
			with conn:
				conn.execute(query)
		except:
			print(f'{bf.FAIL}[EXECUTE_QUERY EXCEPTION]{bf.ENDC}: {bf.WARNING}query={query}{bf.ENDC}')
			raise
		
	def execute_select(self, query):
		try:
			conn = sqlite3.connect(self.db)
			results = []
			with conn:
				results = conn.execute(query).fetchall()
			return results	
		except:
			print(f'{bf.FAIL}[EXECUTE_SELECT EXCEPTION]{bf.ENDC}: {bf.WARNING}query={query}{bf.ENDC}')
			raise

	# ADD	
		
	def add_chat_id(self, chat_id, secret):
		query = f'INSERT INTO USERS VALUES ({chat_id}, 0, "{secret}");'
		self.execute_query(query)	
		
	def add_chat_id_alt(self, chat_id_alt, secret):
		query = f'UPDATE users SET CHAT_ID_ALT = {chat_id_alt} WHERE SECRET = "{secret}"'
		self.execute_query(query)

	def add_word(self, chat_id, word, last, delta):
		query = f'REPLACE INTO user_words VALUES({chat_id}, "{word}", {last}, {delta})'
		self.execute_query(query)	            
		
	def add_translation(self, word, tr):
		query = f'REPLACE INTO word_translation VALUES ("{word}", "{tr}")'
		self.execute_query(query)

	def add_examples(self, word, es):
		for e in es:
			query = f'INSERT INTO word_examples VALUES("{word}", "{e}");'
			self.execute_query(query)

	# SELECT

	def select_record_for_secret(self, secret):
		query = f'SELECT * FROM users WHERE SECRET = "{secret}"'
		r = self.execute_select(query)
		return r[0] if len(r) else None

	def select_chat_id(self, chat_id_alt):
		query = f'SELECT CHAT_ID FROM users WHERE CHAT_ID_ALT = {chat_id_alt}'
		r = self.execute_select(query)
		return r[0][0] if len(r) else None
				      
	def select_records(self, chat_id):
		query = f'SELECT WORD, LAST, DELTA FROM user_words WHERE CHAT_ID = {chat_id}'
		return self.execute_select(query)

	def select_translation(self, word):
		query = f'SELECT TRANSLATION FROM word_translation WHERE WORD = "{word}"'
		r = self.execute_select(query)
		return r[0][0] if len(r) else None

	def select_examples(self, word):
		query = f'SELECT EXAMPLE FROM word_examples WHERE WORD = "{word}"'
		results = self.execute_select(query)
		return [r[0] for r in results]

	def select_chat_id_alts(self):
		query = f'SELECT CHAT_ID_ALT FROM users'
		results = self.execute_select(query)
		return [r[0] for r in results]
			
	# UPDATE
	
	def pend(self, chat_id_alt):
		query = f'REPLACE INTO user_pending VALUES({chat_id_alt}, 1);'
		self.execute_query(query)
	
	def unpend(self, chat_id_alt):
		query = f'REPLACE INTO user_pending VALUES({chat_id_alt}, 0);'
		self.execute_query(query)
	
	def unpend_everyone(self):
		query = f'UPDATE user_pending SET IS_PENDING = 0'
		self.execute_query(query)
		
	def remove(self, chat_id_alt):
		query = f'UPDATE users SET CHAT_ID_ALT=0 WHERE CHAT_ID_ALT={chat_id_alt}'
		self.execute_query(query)
		
	def remove_word(self, chat_id, word):
		query = f'DELETE FROM user_words WHERE CHAT_ID={chat_id} AND WORD="{word}"'
		self.execute_query(query)
			       
	# CHECKS
	
	def check_chat_id(self, chat_id):
		query = f'SELECT CHAT_ID FROM users WHERE CHAT_ID = {chat_id}'
		return len(self.execute_select(query)) > 0
		
	def check_word(self, chat_id, word):
		query1 = f'SELECT CHAT_ID, WORD, LAST, DELTA FROM user_words WHERE CHAT_ID = {chat_id} AND WORD = "{word}"'
		r = self.execute_select(query1)
		if len(r) > 0:
			r = r[0]
			r = {'chat_id' : r[0], 'word' : r[1], 'last' : r[2], 'delta' : r[3]}
		else: 
			r = None

		query2 = f'SELECT WORD FROM word_translation WHERE WORD = "{word}"'
		return r is not None, r, len(self.execute_select(query2)) > 0
		
	def check_pending(self, chat_id_alt):
		query = f'SELECT IS_PENDING FROM user_pending WHERE CHAT_ID_ALT = {chat_id_alt}'
		r = self.execute_select(query)
		return bool(r[0][0]) if len(r) else None

