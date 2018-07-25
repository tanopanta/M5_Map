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

# ここからウェブアプリケーション用のルーティングを記述
# index にアクセスしたときの処理
@app.route('/')
def index():
    # index.html をレンダリングする
    return render_template('index.html', api_key=API_KEY)

@app.route('/get_geo', methods=['GET'])
def get_geo():
    latlngs = geo.get_latlngs(API_KEY)

    obj = {
        "latlngs": [
        {
            "lat": 35.681167, 
            "lng": 139.767052
        },
        {
            "lat": 35.682592,
            "lng": 139.767052
        }
        ]
    }
    return Response(json.dumps(obj))

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    #app.run(host='0.0.0.0') # どこからでもアクセス可能に
    app.run()
