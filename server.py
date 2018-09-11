import json
import os
import sqlite3
import time
from datetime import datetime

#from dotenv import load_dotenv
from flask import Flask, Response, g, redirect, render_template, request, url_for

import geo

# 自身の名称を app という名前でインスタンス化する
app = Flask(__name__)

#load_dotenv()
#API_KEY = os.environ.get("MAP_API_KEY") #.envファイルに記入
API_KEY = "test"
DATABASE = "database.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        #コネクションを確保
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ここからウェブアプリケーション用のルーティングを記述
# index にアクセスしたときの処理
@app.route('/')
def index():
    # index.html をレンダリングする
    return render_template('index.html', api_key=API_KEY)

@app.route('/person')
def person():
    return render_template('person.html', api_key=API_KEY)

@app.route('/get_geo', methods=['GET'])
def get_geo():
    #URLにパラメータtime(unixtimeで指定)がついているとき、time以降のデータのみ取り出す
    time_later = request.args.get("time", type=int)
    if not time_later:
        time_later = int(time.time()) - 60 #デフォルトは60秒分
    
    db = get_db()
    c = db.cursor()
    objects = []

    for row in c.execute("select * from data where date > ?", (time_later,)):
        print(row)
        date = datetime.fromtimestamp(row[1]).strftime("%Y/%m/%d %H:%M:%S")
        objects.append({"date":date, "lat":row[2], "lng":row[3], "stress":row[4], "bpm":row[6]})
    obj = {
        "objects": objects
    }

    return Response(json.dumps(obj))
@app.route('/post_geo', methods=['POST'])
def post_geo():
    js = request.json #辞書型で取得

    db = get_db()
    c = db.cursor()
    args = ('wawawa', int(datetime.now().timestamp()), js["lat"],js["lng"],  js["stress"], "立ち", js["bpm"])
    c.execute("""insert into data values
        (?,?,?,?,?,?,?)""", args)
    db.commit()
    
    return Response(json.dumps({"result":"OK"}))

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に
    #app.run()
