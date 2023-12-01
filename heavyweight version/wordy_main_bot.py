import random
import time

import threading

from custom_logs import log_user_word, log_user_answer, log_user_opinion, log_exception, log_user_hint

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

def encrypt_data(chat_id, word, handle_option, mode=None, delta=None, verdict=None):
	data = f"cid:{chat_id}#w:{word}#h:{handle_option}"
	if mode is not None:
		data += f"#m:{mode}"
	if verdict is not None:
		data += f"#v:{verdict}"
	if verdict is not None:
		data += f"#d:{delta}"
	return data

def decrypt_data(data):
	dct = {}
	key_vals = data.split("#")
	for kv in key_vals:
		k, v = kv.split(':')
		if k in ["d", "cid" ,"depth"]:
			v = int(v)
		dct[k] = v
	return dct

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

# this is to handle handle_option:opinion, or shortly h:o
@bot.callback_query_handler(func=lambda call: 'h:o' in call.data)
def handle_call(call):
	chat_id_alt = call.message.chat.id
	data = decrypt_data(call.data)
	mode = data['m']
	word = data['w']
	delta = data['d']
	verdict = data['v']
	chat_id = data['cid']
	log_user_opinion(chat_id_alt, word, mode)
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
	except Exception as e:
		log_exception(e, "handle_call:opinion")

def gen_opinion_markup(data):
	keyboard = types.InlineKeyboardMarkup()
	keyboard.row_width = 2
	keyboard.add(
		types.InlineKeyboardButton("EASY",   callback_data='m:E' + "#" + data),
		types.InlineKeyboardButton("MEDIUM", callback_data='m:M' + "#" + data),
		types.InlineKeyboardButton("HARD",   callback_data='m:H' + "#" + data),
		types.InlineKeyboardButton("🗑️",     callback_data='m:R' + "#" + data))
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
	data = encrypt_data(chat_id, word, 'o', delta=delta, verdict=verdict)
	try:
		bot.send_message(chat_id, text, reply_markup=gen_opinion_markup(data))
	except Exception as e:
		log_exception(e, "user_reply_handler")
	finally:
		bureau.unpend(chat_id_alt)

# this is to handle handle_option:hint, or shortly h:h
@bot.callback_query_handler(func=lambda call: 'h:h' in call.data)
def handle_call(call):
	chat_id_alt = call.message.chat.id
	data = decrypt_data(call.data)
	word = data['w']
	chat_id = data['cid']
	depth = data['depth']
	log_user_hint(chat_id_alt, word)
	def f(i, c):
		if i <= depth - 1 or i + depth >= len(word):
			return c
		return '_'
	hint = ' '.join(f(i, c) for i, c in enumerate(word))
	try:
		bot.send_message(chat_id=chat_id_alt, text=hint)
	except Exception as e:
		log_exception(e, "handle_call:hint")


def gen_hint_markup(data):
	keyboard = types.InlineKeyboardMarkup()
	keyboard.row_width = 2
	keyboard.add(
		types.InlineKeyboardButton("HINT",   callback_data='h:h#depth:1#' + data),
		types.InlineKeyboardButton("BIG HINT",   callback_data='h:h#depth:2#' + data))
	return keyboard


def examine_word(chat_id_alt, record):
	word = record['word']
	log_user_word(chat_id_alt, word)
	chat_id = record['chat_id']
	text = record['translation']
	if record['example'] is not None:
		text += '\n\n' + record['example']
	data = encrypt_data(chat_id, word, 'h')
	try:
		sent_msg = bot.send_message(chat_id_alt, text, reply_markup=gen_hint_markup(data))
		bot.register_next_step_handler(sent_msg, user_reply_handler, record)
	except Exception as e:
		log_exception(e, "examine word")
		bureau.unpend(chat_id_alt)
		if 'bot was blocked by the user' in str(e):
			bureau.remove_user_alt(chat_id_alt)
			print(f'user {chat_id_alt} blocked the bot and was removed')


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

			
