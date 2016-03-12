import os

from telegram import Updater, User, ReplyKeyboardMarkup
import logging
import checker

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKEN = os.environ['TOKEN']

users = dict()


class UserInfo:
    def __init__(self, telegram_user):
        self.user = telegram_user
        self.banks = dict()

    def add_bank(self, bank_id):
        self.banks[bank_id] = Bank(bank_id)

    def remove_bank(self, bank_id):
        self.banks.pop(bank_id)


class Bank:
    def __init__(self, bank_id):
        self.bank_id = bank_id
        self.bank_name = checker.get_bank_name_by_id(bank_id)

    def get_status(self):
        logger.info("Getting status for bank %s" % self.bank_id)
        return checker.get_status(self.bank_id)


def log_params(method_name, update):
    logger.debug("Method: %s\nFrom: %s\nchat_id: %d\nText: %s" %
                 (method_name,
                  update.message.from_user,
                  update.message.chat_id,
                  update.message.text))


def help(bot, update):
    log_params('help', update)
    bot.sendMessage(update.message.chat_id
                    , text="""Поддерживаемые команды:
/help - Помощь
/addbank - Добавить банк в список интересующих
/removebank - Удалить банк из списка интересующих
/getbanksstatuses - Получить информацию о состоянии банков из списка""")


def add_bank_by_name(bot, update, args):
    log_params('add_bank_by_name', update)
    if len(args) == 0:
        bot.sendMessage(update.message.chat_id, text="Использование:\n/addbank [Название]")
        return
    bank_name_guess = " ".join(args)
    bank_ids_name_map = checker.get_bank_ids_name_map_guesses_by_name(bank_name_guess)  # key = id, value = name
    if len(bank_ids_name_map) == 0:
        bot.sendMessage(update.message.chat_id, text="Никогда не слышал о таком банке")
    elif len(bank_ids_name_map) == 1:
        telegram_user = update.message.from_user
        bot.sendMessage(update.message.chat_id, text=add_bank_by_id(telegram_user, list(bank_ids_name_map.keys())[0]))
    else:
        bot.sendMessage(update.message.chat_id,
                        text="Существует несколько банков с похожим названием. Какой вы имели в виду?",
                        reply_markup=(ReplyKeyboardMarkup(get_choose_bank_keyboard(bank_ids_name_map))))


def add_bank_by_id(telegram_user, bank_id):
    if telegram_user.id not in users.keys():
        users[telegram_user.id] = UserInfo(telegram_user)

    user = users[telegram_user.id]
    if bank_id not in user.banks.keys():
        user.add_bank(bank_id)
        return "Банк успешно добавлен"
    else:
        return "Банк уже есть в списке"


def get_choose_bank_keyboard(bank_ids_name_map):
    pass  # TODO


def get_banks_statuses(bot, update, args):
    telegram_user = update.message.from_user
    if telegram_user.id not in users.keys():
        users[telegram_user.id] = UserInfo(telegram_user)

    user = users[telegram_user.id]
    if len(user.banks) < 1:
        bot.sendMessage(update.message.chat_id,
                        text="Список банков пуст. Сперва добавьте банк в список с помощью команды\n"
                             "/addbank [Название]")
    else:
        for bank in user.banks:
            bot.sendMessage(update.message.chat_id, text=bank.get_status())


def remove_bank(bot, update, args):
    telegram_user = update.message.from_user
    if telegram_user.id not in users.keys():
        users[telegram_user.id] = UserInfo(telegram_user)

    user = users[telegram_user.id]
    if len(user.banks) < 1:
        bot.sendMessage(update.message.chat_id,
                        text="Список банков пуст. Сперва добавьте банк в список с помощью команды\n"
                             "/addbank [Название]")
    else:
        bank_ids_name_map = dict()
        for bank in user.banks.values():
            bank_ids_name_map[bank.bank_id] = bank.bank_name
        bot.sendMessage(update.message.chat_id,
                        text="Выберите банк",
                        reply_markup=(ReplyKeyboardMarkup(get_choose_bank_keyboard(bank_ids_name_map))))


def remove_bank_by_id(telegram_user, bank_id):
    if telegram_user.id not in users.keys():
        users[telegram_user.id] = UserInfo(telegram_user)

    user = users[telegram_user.id]
    if bank_id not in user.banks.keys():
        user.remove_bank(bank_id)
        return "Банк успешно удален"
    else:
        return "Банка не было в списке"


bot_functions = {"help": help, "addbank": add_bank_by_name, "removebank": remove_bank,
                 "getbanksstatuses": get_banks_statuses}


def main():
    updater = Updater(TOKEN)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers for Telegram messages
    for (name, f) in bot_functions.items():
        dp.addTelegramCommandHandler(name, f)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
