import os
import checker
from telegram import Bot

TOKEN = os.environ['TOKEN']


def notify_users():
    subscriptions = checker.get_subscriptions()
    bot = Bot(TOKEN)
    users = set()
    for (user_id, bank_id) in subscriptions:
        if user_id not in users:
            users.add(user_id)
            bot.sendMessage(chat_id=user_id, text="Обновились данные о финансовом состоянии интересующих вас банков")

    for (user_id, bank_id) in subscriptions:
        bot.sendMessage(chat_id=user_id, text=checker.get_status(bank_id))
