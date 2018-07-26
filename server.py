import json
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, url_for

import geo

# 自身の名称を app という名前でインスタンス化する
app = Flask(__name__)

load_dotenv()
API_KEY = os.environ.get("MAP_API_KEY") #.envファイルに記入

latlngs = []

# ここからウェブアプリケーション用のルーティングを記述
# index にアクセスしたときの処理
@app.route('/')
def index():
    # index.html をレンダリングする
    return render_template('index.html', api_key=API_KEY)

@app.route('/get_geo', methods=['GET'])
def get_geo():
    global latlngs
    obj = {
        "latlngs": latlngs
    }
    latlngs = []
    return Response(json.dumps(obj))
@app.route('/post_geo', methods=['POST'])
def post_geo():
    latlngs.append(request.json)
    return Response(json.dumps({"result":"OK"}))

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に
    #app.run()
