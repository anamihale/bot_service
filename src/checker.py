import os

import psycopg2

# Try to connect
cur = None
conn = None
try:
    password = os.environ['ESCAPEBANKDBPASS']
    conn = psycopg2.connect("host='localhost' dbname='escapebank' user='postgres' password='%s'" % password)
    cur = conn.cursor()
except Exception as err:
    print("I am unable to connect to the database: ", str(err))


def add_subscription(user_id, bank_id):
    print("Adding subscrition", user_id, bank_id)
    cur.execute("SELECT * FROM subscriptions WHERE user_id=%s AND bank_id=%s", (user_id, bank_id))
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.execute("INSERT INTO subscriptions VALUES (%s, %s)", (user_id, bank_id))
        print(cur.query)
        conn.commit()
        return "Банк добавлен в список"
    else:
        return "Банк уже есть в списке"


def remove_subscription(user_id, bank_id):
    cur.execute("SELECT * FROM subscriptions WHERE user_id=%s AND bank_id=%s", (user_id, bank_id))
    print(cur.query)
    rows = cur.fetchall()
    if len(rows) != 0:
        cur.execute("DELETE FROM subscriptions WHERE user_id=%s AND bank_id=%s", (user_id, bank_id))
        print(cur.query)
        conn.commit()
        return "Банк удален из списка"
    else:
        return "Банк не был в списке"


def remove_user(user_id):
    cur.execute("DELETE FROM subscriptions WHERE user_id=%s", (user_id,))
    print(cur.query)
    conn.commit()


def get_user_subscriptions(user_id):
    cur.execute("SELECT bank_id FROM subscriptions WHERE user_id=%s", (user_id,))
    banks = set()
    for rec in cur:
        banks.add(rec[0])
    return banks


def get_bank_name(bank_id):
    cur.execute("SELECT name FROM banks WHERE id=%s", (bank_id,))
    return cur.fetchone()[0]


def get_bank_id(bank_name):
    cur.execute("SELECT id FROM banks WHERE name=%s", (bank_name,))
    return cur.fetchone()[0]


def get_bank_name_guesses(bank_name):
    cur.execute("SELECT id FROM synonyms WHERE name LIKE '%" + bank_name + "%'")
    print(cur.query)
    banks = set()
    for rec in cur:
        banks.add(rec[0])
    return banks


def get_bank_names():
    names = set()
    cur.execute("SELECT name FROM banks")
    for rec in cur:
        names.add(rec[0])
    return names


def get_norm_values(bank_id):
    norm_values = set()
    cur.execute("SELECT norm,value,date FROM norm_values WHERE id=%s", (bank_id,))
    for rec in cur:
        norm_values.add((rec[0], rec[1], rec[2]))
    return norm_values


def get_status(bank_id):
    return "Банк .... \n" \
           "За последние полгода нормативы нарушались 6 раз (по нормативу Н1 - 5 раз, по нормативу Н2 - 1 раз)"
