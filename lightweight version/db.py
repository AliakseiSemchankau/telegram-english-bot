import sqlite3
from pprint import pprint

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import bcolors as bf

class SQL:

	def create(self, db):
		conn = sqlite3.connect(db)
		print("Opened database successfully")
		with conn:
			conn.execute('''CREATE TABLE users
					(CHAT_ID       INT PRIMARY KEY    NOT NULL);
					''')

			conn.execute('''CREATE TABLE user_words
					(CHAT_ID       INT                NOT NULL,
					WORD           TEXT               NOT NULL,
					LAST           INT                NOT NULL,
					DELTA          INT                NOT NULL);
					''')

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
		
	def add_chat_id(self, chat_id):
		query = f'INSERT INTO USERS VALUES ({chat_id});'
		self.execute_query(query)	

	def add_word(self, chat_id, word, last, delta):
		query = f'REPLACE INTO user_words VALUES({chat_id}, "{word}", {last}, {delta})'
		self.execute_query(query)	            

	# SELECT
				      
	def select_records(self, chat_id):
		query = f'SELECT WORD, LAST, DELTA FROM user_words WHERE CHAT_ID = {chat_id}'
		return self.execute_select(query)
			
	# UPDATE
		
	def remove_word(self, chat_id, word):
		query = f'DELETE FROM user_words WHERE CHAT_ID={chat_id} AND WORD="{word}"'
		self.execute_query(query)
			       
	# CHECKS
	
	def check_chat_id(self, chat_id):
		query = f'SELECT CHAT_ID FROM users WHERE CHAT_ID = {chat_id}'
		return len(self.execute_select(query)) > 0