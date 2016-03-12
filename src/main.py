import os

from telegram import Updater, User, ReplyKeyboardMarkup, ReplyKeyboardHide
import logging
import checker

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKEN = os.environ['TOKEN']

users = dict() #TODO server-side

reply_awaiting_function = None


class UserInfo:
    def __init__(self, telegram_user):
        #TODO server-side
        self.user = telegram_user
        self.banks = dict()

    def add_bank(self, bank_name):
        #TODO server-side
        self.banks[bank_name] = Bank(bank_name)

    def remove_bank(self, bank_name):
        #TODO server-side
        self.banks.pop(bank_name)


class Bank:
    def __init__(self, bank_name):
        self.bank_name = bank_name
        self.bank_id = checker.get_bank_id_by_name(bank_name)

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
    bot.sendMessage(update.message.chat_id, text="""Поддерживаемые команды:
/help - Помощь
/addbank - Добавить банк в список интересующих
/removebank - Удалить банк из списка интересующих
/getbanksstatuses - Получить информацию о состоянии банков из списка""", reply_markup=ReplyKeyboardHide())


def add_bank(bot, update, args):
    global reply_awaiting_function
    log_params('add_bank', update)
    if len(args) == 0:
        bot.sendMessage(update.message.chat_id, text="Использование:\n/addbank [Название]")
        return
    bank_name_guess = " ".join(args)
    bank_names_guesses_list = checker.get_bank_name_guesses(bank_name_guess)  # key = id, value = name
    if len(bank_names_guesses_list) == 0:
        bot.sendMessage(update.message.chat_id, text="Никогда не слышал о таком банке")
    elif len(bank_names_guesses_list) == 1:
        telegram_user = update.message.from_user
        bot.sendMessage(update.message.chat_id, text=add_bank_by_name(telegram_user, bank_names_guesses_list[0]))
    else:
        reply_awaiting_function = "add_bank"
        bot.sendMessage(update.message.chat_id,
                        text="Существует несколько банков с похожим названием. Какой вы имели в виду?",
                        reply_markup=(ReplyKeyboardMarkup(get_choose_bank_keyboard(bank_names_guesses_list))))


def add_bank_by_name(telegram_user, bank_name):
    if telegram_user.id not in users.keys():
        users[telegram_user.id] = UserInfo(telegram_user)

    user = users[telegram_user.id]
    if bank_name not in user.banks.keys():
        user.add_bank(bank_name)
        return "Банк успешно добавлен"
    else:
        return "Банк уже есть в списке"


def get_choose_bank_keyboard(bank_names_list):
    return ReplyKeyboardMarkup(keyboard=[[i] for i in bank_names_list], one_time_keyboard=True, selective=True,
                               resize_keyboard=True)


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


def remove_bank(bot, update):
    global reply_awaiting_function
    telegram_user = update.message.from_user
    if telegram_user.id not in users.keys():
        users[telegram_user.id] = UserInfo(telegram_user)

    user = users[telegram_user.id]
    if len(user.banks) < 1:
        bot.sendMessage(update.message.chat_id,
                        text="Список банков пуст. Сперва добавьте банк в список с помощью команды\n"
                             "/addbank [Название]")
    else:
        reply_awaiting_function = "remove_bank"
        bot.sendMessage(update.message.chat_id,
                        text="Выберите банк",
                        reply_markup=(get_choose_bank_keyboard(user.banks.keys())))


def remove_bank_by_name(telegram_user, bank_name):
    bank_id = checker.get_bank_name_guesses(bank_name)
    if telegram_user.id not in users.keys():
        users[telegram_user.id] = UserInfo(telegram_user)

    user = users[telegram_user.id]
    if bank_name not in user.banks.keys():
        user.remove_bank(bank_id)
        return "Банк успешно удален"
    else:
        return "Банка не было в списке"


bot_functions = {"help": help, "addbank": add_bank, "removebank": remove_bank,
                 "getbanksstatuses": get_banks_statuses}


def bank_name_answer_handler(bot, update, args):
    global reply_awaiting_function
    if reply_awaiting_function == "remove_bank":
        bot.sendMessage(update.message.chat_id,
                        text=remove_bank_by_name(update.message.from_user, update.message.text),
                        reply_markup=ReplyKeyboardHide())
    elif reply_awaiting_function == "add_bank":
        bot.sendMessage(update.message.chat_id,
                        text=add_bank_by_name(update.message.from_user, update.message.text),
                        reply_markup=ReplyKeyboardHide())

    reply_awaiting_function = None


def main():
    updater = Updater(TOKEN)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers for Telegram commands
    for (name, f) in bot_functions.items():
        dp.addTelegramCommandHandler(name, f)

    dp.addTelegramMessageHandler(bank_name_answer_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
