from datetime import date, timedelta
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


def get_subscriptions():
    cur.execute("SELECT * FROM subscriptions")
    subscriptions = set()
    for rec in cur:
        subscriptions.add((rec[0], rec[1]))
    return subscriptions


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




def get_status(bank_id):
    def is_violation(norms, value):
        violations = {'total': 0}
        for norm in norms:
            violations[norm[1]] = 0
        for n in norms:
            n_date = n[0].split(sep='/')
            n_date = date(int(n_date[2]), int(n_date[0]), int(n_date[1]))
            for val in value:
                if n[1] == val[0] and n_date >= val[2]:
                    if n[3] == 'max' and float(val[1]) > float(n[2]) or n[3] == 'min' and float(val[1]) < float(n[2]):
                        violations['total'] += 1
                        violations[n[1]] += 1
        return violations

    norms = [['01/01/2001', 'Н1.0', '10', 'min'], ['01/01/2001', 'Н1.1', '5', 'min'],
             ['01/01/2001', 'Н1.2', '5.5', 'min'], ['01/01/2001', 'Н2', '15', 'min'], ['01/01/2001', 'Н3', '50', 'min'],
             ['01/01/2001', 'Н4', '120', 'max'], ['01/01/2001', 'Н6', '25', 'max'], ['01/01/2001', 'Н7', '800', 'max'],
             ['01/01/2001', 'Н9.1', '50', 'max'], ['01/01/2001', 'Н10.1', '3', 'max'],
             ['01/01/2001', 'Н12', '25', 'max'], ['01/01/2001', 'Н15', '100', 'min'],
             ['01/01/2001', 'Н16', '100', 'max'], ['01/01/2001', 'Н16.1', '0', 'max'],
             ['01/01/2001', 'Н18', '100', 'min'], ['01/01/2015', 'Н1.2', '6', 'min'],
             ['01/01/2016', 'Н1.0', '8', 'min'], ['01/01/2016', 'Н1.1', '4.5', 'min']]

    vals = get_norm_values(bank_id)

    l_vals = sorted(vals, key=lambda x: x[2], reverse=True)
    final_date = l_vals[0][2]

    count = 0
    while count < len(l_vals) and l_vals[count][2] > final_date - timedelta(days=182):
        count += 1
    l_vals = l_vals[:count]
    violations = is_violation(norms, l_vals)

    if violations['total'] == 0:
        half_year = "У банка за за полгода до %s наружений не было" % final_date
    else:
        half_year = "Всего за полгода до %s у банка было %d нарушений. Из них нарушены: \n" % (
            final_date, violations['total'])
        for key, value in violations.items():
            if key != 'total' and value != 0:
                half_year += "норматив %s - %d раз \n" % (key, value)

    count_m = 0
    while count_m < len(l_vals) and l_vals[count_m][2] > final_date - timedelta(days=30):
        count_m += 1
    l_vals = l_vals[:count_m]
    violations_m = is_violation(norms, l_vals)

    total_violations_m = violations_m['total'] == 0
    if total_violations_m:
        month = "У банка за за месяц до %s наружений не было" % final_date
    else:
        month = "Всего за месяц до %s у банка было %d нарушений. Из них нарушены:\n" % (
            final_date, violations_m['total'])
        for key, value in violations_m.items():
            if key != 'total' and value != 0:
                month += "норматив %s - %d раз \n" % (key, value)

    signal = ""
    if total_violations_m and violations['total'] - violations_m['total'] == 0:
        signal = "Зеленый сигнал. Опасности нет.\n"
    elif total_violations_m and violations['total'] - violations_m['total'] != 0:
        signal = "Желтый сигнал опасности. У банка недавно были нарушения.\n"
    elif not total_violations_m and violations['total'] - violations_m['total'] == 0:
        signal = "Оранжевый сигнал опасности. У банка появились нарушения.\n"
    elif not total_violations_m and violations['total'] - violations_m['total'] != 0:
        signal = "Красный сигнал опасности. Нарушения существуют длительное время.\n"

    return signal, month, half_year
