import os

from telegram import Updater, User, ReplyKeyboardMarkup, ReplyKeyboardHide
import logging
import checker

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TOKEN = os.environ['TOKEN']
reply_awaiting_function = None
all_banks = checker.get_bank_names()


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
/getbanksstatuses - Получить информацию о состоянии банков из списка
/stop - Прекратить получать уведомления, очистить список""", reply_markup=ReplyKeyboardHide())


def add_bank(bot, update, args):
    global reply_awaiting_function
    log_params('add_bank', update)
    if len(args) == 0:
        reply_awaiting_function = add_subscription
        bot.sendMessage(update.message.chat_id, text="Использование:\n/addbank [Название]\n"
                                                     "Но может быть вам повезет и банк будет в предложеном списке",
                        reply_markup=(get_choose_bank_keyboard(sorted(list(all_banks)[:10]))))
    else:
        user_guess = " ".join(args)
        bank_names_guesses_list = sorted([checker.get_bank_name(i) for i in checker.get_bank_name_guesses(user_guess)])
        if len(bank_names_guesses_list) == 0:
            bot.sendMessage(update.message.chat_id, text="Никогда не слышал о таком банке")
        elif len(bank_names_guesses_list) == 1:
            telegram_user = update.message.from_user.id
            reply = add_subscription(telegram_user, bank_names_guesses_list[0])
            bot.sendMessage(update.message.chat_id, text=reply)
        else:
            reply_awaiting_function = add_subscription
            bot.sendMessage(update.message.chat_id,
                            text="Существует несколько банков с похожим названием. Какой вы имели в виду?",
                            reply_markup=(get_choose_bank_keyboard(bank_names_guesses_list)))


def add_subscription(telegram_user_id, bank_name):
    if bank_name in all_banks:
        return checker.add_subscription(telegram_user_id, checker.get_bank_id(bank_name))
    else:
        return "Никогда не слышал о таком банке"


def get_choose_bank_keyboard(bank_names_list):
    return ReplyKeyboardMarkup(keyboard=[[i] for i in bank_names_list], one_time_keyboard=True, selective=True,
                               resize_keyboard=True)


def get_banks_statuses(bot, update, args):
    telegram_user = update.message.from_user.id
    user_banks_ids = checker.get_user_subscriptions(telegram_user)
    if len(user_banks_ids) < 1:
        bot.sendMessage(update.message.chat_id,
                        text="Список банков пуст. Сперва добавьте банк в список с помощью команды\n"
                             "/addbank [Название]")
    else:
        for bank_id in user_banks_ids:
            bot.sendMessage(update.message.chat_id, text=checker.get_status(bank_id))


def remove_bank(bot, update):
    global reply_awaiting_function
    telegram_user = update.message.from_user.id
    user_banks_names = [checker.get_bank_name(bank_id) for bank_id in checker.get_user_subscriptions(telegram_user)]
    if len(user_banks_names) < 1:
        bot.sendMessage(update.message.chat_id,
                        text="Список банков пуст. Сперва добавьте банк в список с помощью команды\n"
                             "/addbank [Название]")
    else:
        reply_awaiting_function = remove_subscription
        bot.sendMessage(update.message.chat_id,
                        text="Выберите банк",
                        reply_markup=(get_choose_bank_keyboard(user_banks_names)))


def remove_subscription(telegram_user_id, bank_name):
    if bank_name in all_banks:
        return checker.remove_subscription(telegram_user_id, checker.get_bank_id(bank_name))
    else:
        return "Никогда не слышал о таком банке"


def stop(bot, update):
    checker.remove_user(update.message.from_user.id)
    bot.sendMessage(update.message.chat_id,
                    text="Вы всегда можете начать общение со мной заново по команде /start",
                    reply_markup=ReplyKeyboardHide())

bot_functions = {"help": help, "addbank": add_bank, "removebank": remove_bank,
                 "getbanksstatuses": get_banks_statuses, "stop": stop}


def bank_name_answer_handler(bot, update, args):
    global reply_awaiting_function
    if reply_awaiting_function is not None:
        # noinspection PyCallingNonCallable
        reply = reply_awaiting_function(update.message.from_user.id, update.message.text)
        bot.sendMessage(update.message.chat_id,
                        text=reply,
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
