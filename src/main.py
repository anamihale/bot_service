from telegram import Updater, User, ReplyKeyboardMarkup
import logging
import checker

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKEN = '199327503:AAEfqxWvl5QzS8dxq98ndrPDkCKechgaths'

users = dict()


class UserInfo:
    def __init__(self, telegram_user):
        self.user = telegram_user
        self.banks = {}

    def add_bank(self, bank_id):
        self.banks[bank_id] = Bank(bank_id)


class Bank:
    def __init__(self, bank_id):
        self.bank_id = bank_id

    def get_norm_violation(self):
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


def get_bank_id_guesses_by_name(bank_name):
    return dict()  # TODO


def add_bank_by_name(bot, update, args):
    log_params('add_bank_by_name', update)
    if len(args) == 0:
        bot.sendMessage(update.message.chat_id, text="Использование:\n/addbank [Название]")
        return
    bank_name_guess = " ".join(args)
    bank_ids_name_map = get_bank_id_guesses_by_name(bank_name_guess)  # key = id, value = name
    if len(bank_ids_name_map) == 0:
        bot.sendMessage(update.message.chat_id, text="Никогда не слышал о таком банке")
    elif len(bank_ids_name_map) == 1:
        telegram_user = update.message.from_user
        bot.sendMessage(update.message.chat_id, text=add_bank_by_id(telegram_user, bank_ids_name_map.values()[0]))
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
    pass  # TODO


def remove_bank_by_id(bot, update, args):
    pass  # TODO


def main():
    updater = Updater(TOKEN)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handlers for Telegram messages
    for (name, f) in bot_functions:
        dp.addTelegramCommandHandler(name, f)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

bot_functions = {"help": help, "addbank": add_bank_by_name, "removebank": remove_bank_by_id,
                 "getbanksstatuses": get_banks_statuses}
