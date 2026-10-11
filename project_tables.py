import sqlite3


conobj = sqlite3.connect(database='bank.sqlite')
curobj = conobj.cursor()


table1 = '''
CREATE TABLE IF NOT EXISTS accounts(
    accounts_acno INTEGER PRIMARY KEY AUTOINCREMENT,
    accounts_name TEXT,
    accounts_pass TEXT,
    accounts_email TEXT,
    accounts_mob TEXT,
    accounts_gender TEXT,
    accounts_opendate TEXT,
    accounts_bal FLOAT
)
'''


table2 = '''
CREATE TABLE IF NOT EXISTS stmts(
    stmts_acn INTEGER,
    stmts_amt FLOAT,
    stmts_type TEXT,
    stmts_date TEXT,
    stmts_update_bal FLOAT,
    stmts_txnid TEXT PRIMARY KEY
)
'''


try:
    curobj.execute(table1)
    curobj.execute(table2)
    conobj.commit()
    print('Tables created successfully')

except Exception as msg:
    print(msg)

finally:
    conobj.close()