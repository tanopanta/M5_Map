import json
import math
import os
import queue
import signal
import subprocess
import threading
import time
import urllib.request

import numpy as np
import scipy.signal as sg
from dotenv import load_dotenv
from scipy import integrate
from scipy.interpolate import interp1d

import grovepi2 as grovepi

addr = "192.168.1.2"
fs_pulse = 512
fs_acc = 64
buff_size = fs_pulse * 60
acc_interval = fs_pulse // fs_acc #8


def task(arg1, arg2):
    #タイマー処理
    #taskにかかる最大時間 << タイマ周期じゃないとだめ
    
    global count
    global data
    global acc_data
    count += 1
    
    sensor_value = grovepi.analogRead(1)

    if count % acc_interval == 0:
        acc = grovepi.acc_xyz(signed=True) #acc_interval 回に一回だけ加速度を読み取り
        acc_data.append(acc)
        
    data.append(sensor_value)
    
    if len(data) >= buff_size:
        que.put(data)
        #data = data[fs_pulse*10:]
        data = []
        acc_data = []

class SendThread(threading.Thread):
    def run(self) :
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        API_KEY = os.environ.get("MAP_API_KEY") #.envファイルに記入
        assert API_KEY, ".envファイルにMAP_API_KEYを指定してください"
        self.url = "https://www.googleapis.com/geolocation/v1/geolocate?key="+ API_KEY
        while True:
            try:
                #キューからデータを取得する
                pulse = que.get()
            except queue.Empty:
                print("empty")
                break
            stress = self.pulse_to_stress(pulse, fs_pulse, 8, 4096)
            print(stress)
            latlng = self.get_latlngs()
            print(latlng)
            self.post({"lat":latlng[0], "lng":latlng[1], "stress":stress})
    
    def get_latlngs(self):
        iwlist = subprocess.Popen(["sudo", "iwlist", "wlan0", "scan"], stdout=subprocess.PIPE)
        grep = subprocess.Popen(["grep", "-e", "Address:", "-e", "Signal"],
                    stdin=iwlist.stdout, stdout=subprocess.PIPE)
        grep = grep.communicate()[0].splitlines()

        wifiAccessPoints = []

        for add, level in zip(grep[::2], grep[1::2]):
            mac_address = add.split()[4].decode('utf-8')
            signal_level = int(level.split()[2][6:])
            wifiAccessPoints.append({"macAddress":mac_address, "signalStrength":signal_level, "age":0})

        json_data = json.dumps({"wifiAccessPoints":wifiAccessPoints}).encode("utf-8")
        req = urllib.request.Request(url=self.url,data=json_data,headers={'Content-type':'application/json'})

        response = urllib.request.urlopen(req)

        content = json.loads(response.read().decode('utf-8'))
        lat = content['location']['lat']    #緯度
        lng = content['location']['lng']    #経度
        radius = content['accuracy']        #正確さ（半径）
        return lat, lng
    
    def post(self, data):
        obj = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(url="http://"+addr+":5000/post_geo", data=obj, method="POST", headers={"Content-Type" : "application/json"})
        urllib.request.urlopen(request)
    
    def pulse_to_stress(self, pulse, fs, hokan_fs, fft_size):
        peak_indexes, _ = sg.find_peaks(pulse, height=0, distance=fs//3)
        peak_diffs = np.diff(peak_indexes) / fs
        peak_seconds = peak_indexes / fs
        
        f = interp1d(peak_seconds[:-1], peak_diffs, kind="cubic", fill_value='extrapolate')
        new_sample_len = len(pulse) / (fs / hokan_fs)
        xnew = np.linspace(0 , len(pulse) / fs, new_sample_len)
        hokan = f(xnew)
        
        hokan = sg.detrend(hokan, type="constant")
        hokan = hokan[hokan_fs//2:-hokan_fs] #前後1秒分ぐらいをカット
            
        window = np.hanning(len(hokan))
        hokan = hokan * window 

        f = np.fft.fft(hokan, n=fft_size) #fft_size点でfft
        amp = np.abs(f) #a + ib => sqrt(a^2 + b^2)
        pow = amp ** 2 #パワースペクトルに

        #ストレス値計算------------
        lf_min = self.hz_to_idx(0.04, hokan_fs, fft_size)
        lf_max = self.hz_to_idx(0.15, hokan_fs, fft_size)
        hf_min = lf_max # + 1(sumの場合)
        hf_max = self.hz_to_idx(0.4, hokan_fs, fft_size)
        lf = integrate.trapz(pow[lf_min:lf_max+1]) #台形公式による積分
        hf = integrate.trapz(pow[hf_min:hf_max+1]) 
        return lf/hf

    def hz_to_idx(self, hz, fs, point):
        return math.ceil(hz / (fs / (point)))

data = []
acc_data = []

grovepi.acc_init(fs_acc)
count = 0

que = queue.Queue()

thd = SendThread(daemon=True)#デーモンスレッド（メインスレッドと同時に落ちる）
thd.start()

#タイマー処理を設定
signal.signal(signal.SIGALRM, task)
signal.setitimer(signal.ITIMER_REAL, 1 / fs_pulse, 1 / fs_pulse)
print("start CTRL+Cで停止")
try:
    start = time.time()
    while True:
        time.sleep(1)
    raise KeyboardInterrupt()
except KeyboardInterrupt:
    print("end")
    signal.setitimer(signal.ITIMER_REAL, 0)
