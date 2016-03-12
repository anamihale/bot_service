import os

import psycopg2

# Try to connect

try:
    password = os.environ['ESCAPEBANKDBPASS']
    conn = psycopg2.connect("host='localhost' dbname='escapebank' user='postgres' password='%s'" % password)
except:
    print("I am unable to connect to the database.")

cur = conn.cursor()


def get_status(bank_id):
    return "Банк .... \n" \
           "За последние полгода нормативы нарушались 6 раз (по нормативу Н1 - 5 раз, по нормативу Н2 - 1 раз)"


def get_bank_name_guesses(bank_name):
    return []  # TODO


def get_bank_id_by_name(bank_name):
    return None  # TODO
