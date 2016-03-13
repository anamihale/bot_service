import os
import checker
from telegram import Bot

TOKEN = os.environ['TOKEN']

subscriptions = checker.get_subscriptions()
bot = Bot(TOKEN)
users = set()
print(subscriptions)
for (user_id, bank_id) in subscriptions:
    if user_id not in users:
        users.add(user_id)
        print("Оповещаю пользователя ", user_id)
        bot.sendMessage(chat_id=int(user_id),
                        text="Обновились данные о финансовом состоянии интересующих вас банков")

for (user_id, bank_id) in subscriptions:
    text = checker.get_status(bank_id)
    print("Оповещаю пользователя ", user_id, " o том, что \n", text)
    bot.sendMessage(chat_id=int(user_id), text=text)
