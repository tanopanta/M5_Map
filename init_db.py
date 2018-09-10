import sqlite3

#DBの初期化のために実行するコマンド

conn = sqlite3.connect('database.db')
c = conn.cursor()
"""
c.execute('''
        create table if not exists data(
            id text,
            date int,
            lat real,
            lng real,
            stress real,
            act text
            bpm real)''')
"""
#c.execute("alter table data add culumn bpm real")
conn.commit()
conn.close()
print("DB初期化完了！")