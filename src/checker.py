# import psycopg2
#
# # Try to connect
#
# try:
#     conn=psycopg2.connect("dbname='template1' user='dbuser' password='mypass'")
# except:
#     print("I am unable to connect to the database.")
#
# cur = conn.cursor()

def get_bank_name_by_id(bank_id):
    pass  # TODO


def get_status(bank_id):
    return get_bank_name_by_id(bank_id) + "\n" \
                                          "ok"


def get_bank_name_guesses(bank_name):
    return []  # TODO


def get_bank_id_by_name(bank_name):
    return None #TODO