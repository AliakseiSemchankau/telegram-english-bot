import random
import time

from pprint import pprint

import threading

from constants import bcolors as bf

import telebot
from telebot import types
from secrets import MAIN_TOKEN as TOKEN
bot = telebot.TeleBot(TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

from decider import Decider
decider = Decider('test.db')

from bureau import Bureau
bureau = Bureau('test.db')

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



def user_secret_handler(message):
	chat_id_alt = message.chat.id
	secret = message.text
	status, chat_id = bureau.inscrire_user_alt(chat_id_alt, secret)
	bot.send_message(chat_id_alt, f"ID {chat_id_alt}: {status}.\nPaired with ID: {chat_id}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	chat_id_alt = message.chat.id
	sent_message = bot.send_message(chat_id_alt, "secret word?")
	bot.register_next_step_handler(sent_message, user_secret_handler)

def log_user_answer(chat_id_alt, user_answer, answer):
	answer_color = bf.FAIL if user_answer != answer else bf.OKGREEN
	print(f'{bf.OKCYAN}[examine_word]{bf.ENDC}: '
	      f'chat_id_alt={chat_id_alt}, word={bf.OKGREEN}{answer}{bf.ENDC}, answer={answer_color}{user_answer}{bf.ENDC}')

def log_user_opinion(chat_id_alt, word, mode):
	action_color = mode_to_color[mode]
	mode = mode_to_word[mode]
	print(f'{bf.CWHITE}[handle_call]{bf.ENDC}: '
	      f'chat_id_alt={chat_id_alt}, word={bf.OKGREEN}{word}{bf.ENDC}, action={action_color}{mode}{bf.ENDC}')

@bot.callback_query_handler(func=lambda call: True)
def handle_call(call):
	chat_id_alt = call.message.chat.id
	mode, word, delta, verdict, chat_id = call.data.split('#')
	log_user_opinion(chat_id_alt, word, mode)
	delta = int(delta)
	chat_id = int(chat_id)
	record = {'word' : word, 'delta': delta}
	if mode == 'R':
		bureau.remove_word(chat_id, word)
		text = f'word {word} removed'
	else:
		delta = bureau.update_queue(chat_id_alt, record, verdict, mode=mode)
		text = 'CORRECT+' + mode_to_word[mode] if verdict == 'C' else 'INCORRECT'
		text += f'\nanswer={word}'
		text = text + f'\nnext check in {delta // 86400} day(s)'
	try:
		bot.edit_message_text(chat_id=chat_id_alt, text=text, message_id=call.message.message_id)
	except:
		print('something went wrong...')	

def gen_markup(data):
	keyboard = types.InlineKeyboardMarkup()
	keyboard.row_width = 2
	keyboard.add(
		types.InlineKeyboardButton("EASY",   callback_data='E' + "#" + data),
		types.InlineKeyboardButton("MEDIUM", callback_data='M' + "#" + data),
		types.InlineKeyboardButton("HARD",   callback_data='H' + "#" + data),
		types.InlineKeyboardButton("🗑️",     callback_data='R' + "#" + data))
	return keyboard

def user_reply_handler(message, record):
	chat_id_alt = message.chat.id
	chat_id = record['chat_id']
	word = record['word']
	user_answer = message.text.upper()
	log_user_answer(chat_id_alt, user_answer, word)
	verdict = 'C' if user_answer == word else 'I'
	delta = bureau.update_queue(chat_id, record, verdict)
	text = f'CORRECT.' if verdict == 'C' else f'INCORRECT.\nword={word}'
	data = f"{word}#{str(delta)}#{verdict}#{chat_id}"
	try:
		bot.send_message(chat_id, text, reply_markup=gen_markup(data))
	except Exception as e:
		print(e)
	finally:
		bureau.unpend(chat_id_alt)


# bot.edit_message_text(chat_id=CHAT_WITH_MESSAGE, text=NEW_TEXT, message_id=MESSAGE_TO_EDIT)	

def examine_word(chat_id_alt, record):
	print(f'{bf.OKCYAN}[examine_word]{bf.ENDC}: chat_id_alt={chat_id_alt}, word=' + f'{bf.OKGREEN}' + record['word'] + f'{bf.ENDC}')
	chat_id = record['chat_id']
	text = record['translation']
	if record['example'] is not None:
		text += '\n\n' + record['example']
	try:
		sent_msg = bot.send_message(chat_id_alt, text)
		bot.register_next_step_handler(sent_msg, user_reply_handler, record)
	except Exception as e:
		print(e)	
		bureau.unpend(chat_id_alt)
		if 'bot was blocked by the user' in str(e):
			bureau.remove_user_alt(chat_id_alt)

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
			bureau.pend(chat_id_alt)
			examine_word(chat_id_alt, record)

			
