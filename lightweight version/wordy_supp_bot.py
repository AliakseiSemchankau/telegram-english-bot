import random
import time
import re

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from constants import bcolors as bf

import telebot
from secret_tokens import SUPP_TOKEN as TOKEN
bot = telebot.TeleBot(TOKEN, parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

from download import download, download_russian
from custom_logs import log_exception, log_add_word

from bureau import Bureau
bureau = Bureau('test2.db')

def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

@bot.message_handler(commands=['start'])
def send_welcome(message):
	chat_id = message.chat.id
	status, secret = bureau.inscrire_user(chat_id)
	bot.send_message(chat_id, f"ID {chat_id} " + status + f"\nSECRET: {secret}")

@bot.message_handler(func=lambda message: True)
def add_word(message):
	chat_id = message.chat.id
	word = message.text.upper()

	if not word.replace('-', '').isalpha():
		bot.reply_to(message, 'please give ONE word of LATIN letters and hyphens only.\nwords with diacritics do not work (yet).')
		return
	
	is_russian = has_cyrillic(word)
	if not is_russian:
		bureau.inscrire_word(chat_id, word)
		result = download(word)
	else:
		result = download_russian(word)

	if result is None:
			status = 'FAILED'
	else:
		status = 'ADDED'

	log_add_word(status, is_russian, word, result)
	if status == "FAILED":
		msg = ""
	else:
		msg =  '\n\n' + result

	bot.send_message(chat_id, msg)


while True:
	try:
		bot.infinity_polling()
	except Exception as e:
		log_exception(e, "infinity_polling")

