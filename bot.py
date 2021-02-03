from config import settings

import telebot
import language_tool_python

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)
tool = language_tool_python.LanguageToolPublicAPI('ru-RU')


def letter_counter(text: str, letter: str = 'м'):
	return len([x for x in text if x == letter])


def contains_misspelling(text: str):
	matches = tool.check(text)
	for match in matches:
		if match.replacements and match.ruleIssueType == 'misspelling' \
				and letter_counter(match.replacements[0]) < letter_counter(text):
			return True
	return False


@bot.message_handler(func=lambda message: True)
def echo_all(message):
	if contains_misspelling(message.text):
		photo = open('doge.jpg', 'rb')
		bot.send_photo(message.chat.id, photo, reply_to_message_id=message.message_id)


bot.polling()
