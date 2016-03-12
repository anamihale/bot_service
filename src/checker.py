import os

import psycopg2

# Try to connect
cur = None
try:
    password = os.environ['ESCAPEBANKDBPASS']
    conn = psycopg2.connect("host='localhost' dbname='escapebank' user='postgres' password='%s'" % password)
    cur = conn.cursor()
except Exception as err:
    print("I am unable to connect to the database: ", str(err))

cur.execute("""SELECT * FROM banks LIMIT 3""")
rows = cur.fetchall()
for row in rows:
    print("   ", row[0])

def get_status(bank_id):
    return "Банк .... \n" \
           "За последние полгода нормативы нарушались 6 раз (по нормативу Н1 - 5 раз, по нормативу Н2 - 1 раз)"


def get_bank_name_guesses(bank_name):
    return []  # TODO


def get_bank_id_by_name(bank_name):
    return None  # TODO
