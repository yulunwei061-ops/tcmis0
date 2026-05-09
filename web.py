from flask import Flask, render_template, request
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup

# --- 1. Firebase 初始化 (修正 Vercel 重複初始化問題) ---
if not firebase_admin._apps:
    if os.path.exists('serviceAccountKey.json'):
        # 本地開發環境
        cred = credentials.Certificate('serviceAccountKey.json')
    else:
        # Vercel 雲端環境
        firebase_config = os.getenv('FIREBASE_CONFIG')
        if firebase_config:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
        else:
            # 如果連環境變數都沒設，這裡會報錯提醒你
            raise ValueError("找不到 FIREBASE_CONFIG 環境變數")
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)

# --- 2. 路由設定 ---

@app.route("/")
def index():
    link = "<h1>歡迎進入魏郁倫的網站</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    link += "<a href='/welcome?u=郁倫&d=靜宜資管&c=資訊管理導論'>Get傳值</a><hr>"
    link += "<a href=/account>Post傳值</a><hr>"
    link += "<a href=/math>次方與根號計算</a><hr>"
    link += "<a href=/read>讀取Firestore資料</a><hr>"
    link += "<a href=/search_form>教師搜尋系統 (依姓名關鍵字)</a><hr>"
    link += "<a href=/spider1>爬取子青老師本學期課程</a><br>"
    link += "<a href=/movie1>爬取即將上映電影</a><br>"
    link += "<a href=/spidermovie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    link += "<a href=/searchMovie>從資料庫搜尋電影</a><hr>"
    link += "<a href=/road>台中十大肇事路口</a><hr>"
    link += "<a href=/weather>讓使用者輸入欲查詢的縣市,會顯示目前天氣及降雨機率</a><hr>"
    return link

@app.route("/weather", methods=["GET", "POST"])
def weather():
    R = "<h1>縣市天氣查詢</h1>"
    if request.method == "POST":
        city = request.form.get("city").replace("台", "臺")
        # 注意：API Key 建議也放入環境變數比較安全
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName=" + city
        try:
            response = requests.get(url)
            data = response.json()
            location_data = data["records"]["location"][0]
            weather_state = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
            rain_chance = location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
            R += f"<h3>{city} 最新天氣預報</h3><p>目前天氣：{weather_state}</p><p>降雨機率：{rain_chance}%</p>"
            R += "<br><a href='/weather'>重新查詢</a>"
            return R
        except Exception as e:
            return R + f"<p style='color:red;'>查詢失敗：{e}</p><a href='/weather'>返回</a>"
    
    form_html = """<form method="post">請輸入縣市名稱 (例: 臺中市): <input type="text" name="city" required><input type="submit" value="查詢"></form><br><a href="/">返回首頁</a>"""
    return R + form_html

@app.route("/road")
def road():
    R = "<h1>台中市十大肇事路口(113年10月)作者:魏郁倫</h1><br>"
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        Data = requests.get(url, headers=headers, timeout=10)
        JsonData = json.loads(Data.text)
        for item in JsonData:
            R += item["路口名稱"] + ", 原因:" + item["主要肇因"] + "<br>"
    except:
        R += "資料讀取失敗"
    return R

@app.route("/movie1")
def movie1():
    keyword = request.args.get("keyword", "")
    R = f"<h1>電影查詢結果: {keyword}</h1>"
    search_form = f"<form action='/movie1' method='get'>搜尋片名關鍵字: <input type='text' name='keyword'><input type='submit' value='查詢'></form><hr>"
    R = search_form + R
    url = "https://www.atmovies.com.tw/movie/next/"
    data = requests.get(url)
    data.encoding = "utf-8"
    sp = BeautifulSoup(data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    found_count = 0
    for item in result:
        title = item.find("img").get("alt")
        if keyword.lower() in title.lower():
            found_count += 1
            img_url = "https://www.atmovies.com.tw" + item.find("img").get("src")
            intro_url = "https://www.atmovies.com.tw" + item.find("a").get("href")
            R += f"<div><h3>{title}</h3><a href='{intro_url}' target='_blank'>電影介紹頁</a><br><img src='{img_url}' width='200'></div><hr>"
    if found_count == 0: R += "<p>抱歉，找不到符合條件的電影。</p>"
    return R 

@app.route("/spidermovie")
def spidermovie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    try:
        lastUpdate = sp.find(class_="smaller09").text.replace("更新時間：","")
    except:
        lastUpdate = "未知"
    
    result = sp.select(".filmListAllX li")
    total = 0
    for item in result:
        total += 1
        movie_id = item.find("a").get("href").replace("/movie/", "").replace("/", "")
        title = item.find(class_="filmtitle").text
        picture = "http://www.atmovies.com.tw" + item.find("img").get("src")
        hyperlink = "http://www.atmovies.com.tw" + item.find("a").get("href")
        showDate = item.find(class_="runtime").text[5:15]
        doc = {"title": title, "picture": picture, "hyperlink": hyperlink, "showDate": showDate, "lastUpdate": lastUpdate}
        db.collection("電影2B").document(movie_id).set(doc)

    return f"網站最新更新日期:{lastUpdate}<br>總共爬取 {total} 部電影到資料庫"

@app.route("/search_form")
def search_form():
    return "<h2>教師搜尋系統</h2><form action='/read2' method='GET'>請輸入姓名關鍵字: <input type='text' name='keyword' required> <input type='submit' value='開始搜尋'></form><hr><a href='/'>返回首頁</a>"

@app.route("/read2")
def read2():
    Result = ""
    keyword = request.args.get("keyword", "")
    if not keyword: return "請輸入關鍵字！"
    docs = db.collection("靜宜資管").get()
    for doc in docs: 
        teacher = doc.to_dict()
        if keyword in teacher.get("name", ""):
            Result += str(teacher) + "<br>"
    return Result if Result else "查無此人"

@app.route("/read")
def read():
    Result = ""
    docs = db.collection("靜宜資管").get()
    for doc in docs: Result += f"文件內容：{doc.to_dict()}<br>"
    return Result

@app.route("/mis")
def course(): return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/me")
def me(): return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")
    return render_template("welcome.html", name=user, dep = d, course = c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        return f"您輸入的帳號是：{request.form['user']}; 密碼為：{request.form['pwd']}"
    return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        try:
            x, y, opt = float(request.form["x"]), float(request.form["y"]), request.form["opt"]
            if opt == "pow": msg = f"{x} 的 {y} 次方 = {x ** y}"
            elif opt == "root": msg = f"{x} 的 {y} 次方根 = {x ** (1/y)}"
            return f"<h1>計算結果</h1><p>{msg}</p><a href='/math'>重新計算</a>"
        except Exception as e:
            return f"計算出錯：{e}"
    return render_template("math.html")

if __name__ == "__main__":
    app.run(debug=True)
