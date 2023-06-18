from flask import Flask, request, redirect, render_template, session
import os
from werkzeug.security import check_password_hash, generate_password_hash
import json
import settingkey
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
mission = ""
settingkey1 = settingkey.randomstring(10)
print(settingkey1)

# JSON 데이터를 파일에서 불러옵니다.
with open('users.json',encoding='utf-8') as json_file:
    users = json.load(json_file)
with open('points.json',encoding='utf-8') as json_file:
    points = json.load(json_file)
with open('lastcom.json',encoding='utf-8') as json_file:
    lastcom = json.load(json_file)
with open("itemList.json",encoding='utf-8') as json_file:
    il = json.load(json_file)

@app.route("/")
def index():
    if "username" in session: # 세션에 "username"이 있으면 실행
        return redirect("/dashboard") # 대시보드 페이지로 이동
    return redirect("/login") # 세션에 "username"이 없으면 로그인 페이지로 이동

@app.route("/login", methods=["GET", "POST"]) # 로그인 페이지
def login():
    if request.method == "POST": # 로그인 정보 받아오기
        username = request.form["username"] # 아이디
        password = request.form["password"] # 비밀번호 
        if username in users and check_password_hash(users[username], password): # 사용자 정보들 중 로그인 정보가 있으면 실행
            session["username"] = username # 세션의 "username"을 아이디로 설정
            session["point"] = points[username] # 세션의 "point"를 사용자 정보들 중 해당하는 포인트 개수로 설정
            return redirect("/dashboard") # 대시보드 페이지로 이동
        else: # 사용자 정보들 중 로그인 정보가 없으면 실행
            return render_template("login.html",error='잘못된 아이디 또는 비밀번호입니다.') # 오류 메시지 띄우기
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"]) # 회원가입 페이지
def signup():
    if request.method == "POST": # 회원가입 정보 받아오기
        username = request.form["username"] # 아이디
        password = request.form["password"] # 비밀번호
        if username in users: # 동일한 아이디를 사용 중인 사용자가 있을 경우
            return render_template("signup.html",error="이미 사용중인 닉네임 입니다.") # 오류 메시지 띄우기
        else: # 아닐 경우
            users[username] = generate_password_hash(password) # 사용자 정보에 비밀번호를 암호화하여 아이디와 함께 저장
            points[username] = 0 # 사용자의 포인트를 0으로 설정
            lastcom[username] = 0000-00-00 # 마지막 미션 수행일을 0000-00-00으로 설정 (미션 수행 가능하게 하기 위함)
            with open('users.json', 'w') as json_file: # 사용자 정보 파일 갱신
                json.dump(users, json_file)
            with open('points.json','w') as pointss: # 사용자들의 포인트 정보 파일 갱신
                json.dump(points, pointss)
            with open('lastcom.json','w') as lc: # 마지막 미션 수행일 파일 갱신
                json.dump(lastcom,lc)
            return redirect("/login") # 로그인 페이지로 연결
    return render_template("signup.html")

@app.route("/dashboard") # 대시보드 페이지
def protected():
    if "username" in session: # 세션에 아이디가 있을 시에 작동
        username = session['username']
        session['point'] = points[username]
        if session['username'] == "chspa103": # 관리자 계정일 시에 작동
            return render_template("admin.html",key=settingkey1)
        return render_template("index.html",mission=mission)
    else:
        return redirect("/login")

@app.route("/setmission", methods=['POST']) # 미션 설정 페이지
def setmission():
    global mission
    global settingkey1
    if request.method == "POST":
        mission1 = request.form["mission"]
        skey = request.form["settingkey"]
        if skey == settingkey1: # 세팅 비밀번호가 있어야 가능
            mission = mission1
            print(mission)
            return render_template("admin.html",message="세팅이 완료되었습니다.",key=settingkey1)
        else:
            return "잘못된 세팅 비밀번호"

@app.route("/missioncom", methods=['POST','GET']) # 미션 완료 페이지
def missioncom():
    username = session['username']
    c = datetime.datetime.now()
    c1 = c.strftime("%Y-%m-%d")
    if request.method == "GET":
        return render_template("missioncom.html")
    elif request.method == "POST":
        if lastcom[username] != c1:
            lastcom[username] = c1
            with open("lastcom.json",'w') as lc:
                json.dump(lastcom,lc)
            points[username] += 10
            with open('points.json','w') as pointss:
                json.dump(points, pointss)
            return redirect('/dashboard')
        else:
            return render_template('index.html',message = "이미 미션을 완료하였습니다.")

@app.route("/shop") # 상품 교환 페이지
def shop():
    return render_template("shop.html",itemList = il)

@app.route("/buy",methods=['POST']) # 구매 페이지
def buy():
    if "username" in session:
        price = il[request.form['item']]
        with open(f"{request.form['item']}.txt",encoding='utf-8') as sss:
            lines = sss.readlines()
            lines = [ss.rstrip('\n') for ss in lines]
            try:
                a = lines.pop()
            except IndexError:
                return "현재 재고가 없습니다."
            with open(f"{request.form['item']}.txt", "w",encoding='utf-8') as f:
                f.write("")
            with open(f"{request.form['item']}.txt", "a",encoding='utf-8') as f:
                for i in lines:
                    f.write(f"{i}\n")
            if lines != ['']:
                if points[session['username']] >= price:
                    points[session['username']] -= price
                    return f"구매한 제품 코드: {a}"

@app.route("/logout") # 로그아웃
def logout():
    session.pop("username", None)
    return redirect("/")

if __name__ == "__main__":
    app.run()
