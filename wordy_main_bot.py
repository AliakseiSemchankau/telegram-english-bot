import random
import time

from pprint import pprint

import threading

from colors import bcolors as bf

import telebot
from secrets import MAIN_TOKEN as TOKEN
bot = telebot.TeleBot(TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

from decider import Decider
decider = Decider('test.db')

def user_secret_handler(message):
	chat_id_alt = message.chat.id
	secret = message.text
	status, chat_id = decider.register_user_alt(chat_id_alt, secret)
	bot.send_message(chat_id_alt, f"ID {chat_id_alt}: {status}.\nPaired with ID: {chat_id}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	chat_id_alt = message.chat.id
	sent_message = bot.send_message(chat_id_alt, "secret word?")
	bot.register_next_step_handler(sent_message, user_secret_handler)

def user_reply_handler(message, record):
	chat_id_alt = message.chat.id
	chat_id = decider.get_chat_id(chat_id_alt)
	answer = record['word']
	user_answer = message.text.upper()
	verdict = 'CORRECT' if user_answer == answer else 'INCORRECT'
	delta = decider.update_queue(chat_id, record, verdict)
	text = f'CORRECT.\nnext check in {delta // 86400} day(s)' if verdict == 'CORRECT' else f'INCORRECT.\nanswer={answer}'
	answer_color = bf.FAIL if user_answer != answer else bf.OKGREEN
	print(f'{bf.OKCYAN}[examine_word]{bf.ENDC}: '
	      f'chat_id_alt={chat_id_alt}, word={bf.OKGREEN}{answer}{bf.ENDC}, answer={answer_color}{user_answer}{bf.ENDC}, hours={delta // 3600}')
	try:
		bot.send_message(chat_id, text)
	except Exception as e:
		print(e)
	finally:
		decider.unpend(chat_id_alt)
	
def examine_word(chat_id_alt, record):
	print(f'{bf.OKCYAN}[examine_word]{bf.ENDC}: chat_id_alt={chat_id_alt}, word=' + f'{bf.OKGREEN}' + record['word'] + f'{bf.ENDC}')
	chat_id = decider.get_chat_id(chat_id_alt)
	text = record['translation']
	if record['example'] is not None:
		text += '\n\n' + record['example']
	try:
		sent_msg = bot.send_message(chat_id_alt, text)
		bot.register_next_step_handler(sent_msg, user_reply_handler, record)
	except Exception as e:
		print(e)	
		decider.unpend(chat_id_alt)
		if 'bot was blocked by the user' in str(e):
			decider.remove(chat_id_alt)

def bot_polling():
    bot.infinity_polling()

polling_thread = threading.Thread(target=bot_polling)
polling_thread.daemon = True
polling_thread.start()

while True:
	time.sleep(5)
	for chat_id_alt in decider.get_chat_id_alts():
		if chat_id_alt == 0:
			continue
		if not decider.is_pending(chat_id_alt):
			chat_id = decider.get_chat_id(chat_id_alt)
			record = decider.get_word_for_id(chat_id)
			if record is None:
				continue
			decider.pend(chat_id_alt)
			examine_word(chat_id_alt, record)

			
