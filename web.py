from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from bs4 import BeautifulSoup

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>歡迎進入魏郁倫的網站</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>現在日期時間</a><hr>"
    link += "<a href=/me>關於我</a><hr>"
    # 注意：這裡的參數 u 也改成了 郁倫
    link += "<a href=' /welcome?u=郁倫&d=靜宜資管&c=資訊管理導論'>Get傳值</a><hr>"
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
    link += "<a href=/rate>本周新片進DB</a><hr>"
    return link

@app.route("/webhook3", methods=["POST"])
def webhook3():
    # build a request object
    req = request.get_json(force=True)
    # fetch queryResult from json
    action =  req["queryResult"]["action"]
    
    # 這裡也同步更改了機器人的自我介紹
    if (action == "rateChoice"):
        rate =  req["queryResult"]["parameters"]["rate"]
        info = "我是魏郁倫開發的電影聊天機器人,您選擇的電影分級是：" + rate + "，相關電影：\n"

        db = firestore.client()
        collection_ref = db.collection("本週新片含分級")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if rate in dict["rate"]:
                result += "片名：" + dict["title"] + "\n"
                result += "介紹：" + dict["hyperlink"] + "\n\n"
        info += result

    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/road")
def road():
    # 頁面標題作者更改
    R = "<h1>台中市十大肇事路口(113年10月)作者:魏郁倫</h1><br>"
    
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        Data = requests.get(url, headers=headers, timeout=10)
        JsonData = json.loads(Data.text)
        for item in JsonData:
            R += item["路口名稱"] + ",原因:" + item["主要肇因"] + "<br>"
    except Exception as e:
        R += f"資料讀取失敗: {e}"
        
    return R

# ... 其他路由 (rate, weather, movie1, spidermovie, movie, search_form, spider1, read2, read, mis, today, me, welcome, account, math) 保持邏輯不變 ...

if __name__ == "__main__":
    app.run(debug=True)
