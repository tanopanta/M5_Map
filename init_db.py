import sqlite3

#DBの初期化のために実行するコマンド

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
        create table if not exists data(
            id text,
            date int,
            lat real,
            lng real,
            valence real,
            arousal real,
            bpm real
            )''')

#c.execute("alter table data add column bpm real")
conn.commit()
conn.close()
print("DB初期化完了！")