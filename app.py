#!/usr/bin/env python
from asyncio.tasks import wait_for
from time import sleep
from flask import Flask, render_template, request, flash, redirect, url_for, g, session
from flask_bootstrap import Bootstrap
from sqlalchemy.sql.elements import Null
from models import UserForm, LoginForm
from flask_datepicker import datepicker
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import json
from proxy import MyThread, proxy_status, proxies_list, my_browser
from proxy_2 import MyThread_2, user_list
from sqlalchemy_serializer import SerializerMixin
import requests
from bs4 import BeautifulSoup
import os
import pprint
import asyncio
from pyppeteer import launch
import time
class Config(object):
    SECRET_KEY = '78w0o5tuuGex5Ktk8VvVDF9Pw3jv1MVE'

app = Flask(__name__)
app.config.from_object(Config)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/usmle'
app.config['SECRET_KEY'] = "3489wfksf93r2k3lf9sdjkfe9t2j3krl"

Bootstrap(app)
datepicker(app)
db = SQLAlchemy(app)
# browser = Null

state_dict = {}

class country_1(db.Model):
   short = db.Column(db.String(10), primary_key = True)
   country = db.Column(db.String(50))

class country_2(db.Model):
   short = db.Column(db.String(10), primary_key = True)
   country = db.Column(db.String(50))

class country_3(db.Model):
   short = db.Column(db.String(10), primary_key = True)
   country = db.Column(db.String(50))

class User(db.Model, SerializerMixin):  
    __tablename__ = 'user'

    serialize_only = ('name', 'email', 'phone', 'exam', 'dates', 'country', 'locations')
    
    name =  db.Column(db.String(50), nullable = False) 
    email = db.Column(db.String(30), nullable = False) 
    phone = db.Column(db.String(20), nullable = False) 
    exam = db.Column(db.Integer, nullable = False)
    dates = db.Column(db.String(500), nullable = False)
    country = db.Column(db.String(30), nullable = False)
    locations = db.Column(db.String(), nullable = False) 
    status = db.Column(db.Integer, default = 0) 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


    def __init__(self, name, email, phone, exam, dates, country, locations):
        self.name = name
        self.email = email
        self.phone = phone
        self.exam = exam
        self.dates = dates
        self.country = country
        self.locations = locations


class PostalCode(db.Model, SerializerMixin):  
    __tablename__ = 'state_postal_code'

    serialize_only = ('state')
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(50), nullable = False)
    country_code = db.Column(db.String(6), nullable = False)
    state = db.Column(db.String(50), nullable = False) 
    state_code = db.Column(db.String(8), nullable = False)
 
    def __init__(self, country, country_code, state, state_code):
        self.country = country
        self.country_code = country_code
        self.state = state
        self.state_code = state_code

class Proxies(db.Model, SerializerMixin):  
    __tablename__ = 'proxy'

    serialize_only = ('state')
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proxy = db.Column(db.String(30), nullable = False)
    bad = db.Column(db.Integer, nullable = False)
 
    def __init__(self, proxy, bad):
        self.proxy = proxy
        self.bad = bad

class Agency():
    def __init__(self, user_id, stop_flag=False):
        self.user_id = user_id
        self.stop_flag = stop_flag


@app.route('/', methods=['GET', 'POST'])
def admin():
    if not 'username' in session:
        return redirect(url_for("login"))
    users = User.query.order_by(User.name)
    print(request.method)
    return render_template('main.html', users=users)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    # print(request.form['name'] + "::::::" + request.form['password'])
    if request.method == 'POST':
        if os.environ.get('ADMIN_NAME') == request.form['name'] and os.environ.get('ADMIN_PASSWORD') == request.form['password']:
            session['username'] = request.form['name']
            return redirect(url_for('admin'))
   
    return render_template('login.html', form=LoginForm())

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = UserForm(request.form)
    
    if 'type_' in request.form:# == "save":

        if not form.validate_on_submit():
            flash('Please enter all the fields', 'error')
        else:
            str = ''
            for i in range(len(request.form.getlist('td_location[]'))):
                if request.form.getlist('td_location[]')[i]:
                    if str != '' :
                        str += ','
                    str += '{"l": "' + request.form.getlist('td_location[]')[i] +'", '
                    str += '"c": "' + request.form.getlist('td_center_number[]')[i] +'"}'
            str = '{"locationList":[' + str +']}'

            user_ = User(request.form['name'], request.form['email'], request.form['phone'], request.form['exam'], request.form['dates'], request.form['country'], str)
            
            db.session.add(user_)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('admin'))   
    
    form.locations = [{"location": "", "center_number": ""}]
    return render_template('user.html', form=form, )


@app.route('/edit_user', methods=['POST'])
def edit_user():  
    form = UserForm(request.form)
    
    # if request.method == 'POST':
    if request.form['type_'] == "save":
        if not form.validate_on_submit():
            flash('Please enter all the fields', 'error')
        else:
            str = ''
            for i in range(len(request.form.getlist('td_location[]'))):
                if request.form.getlist('td_location[]')[i]:
                    if str != '' :
                        str += ','
                    str += '{"l": "' + request.form.getlist('td_location[]')[i] +'", '
                    str += '"c": "' + request.form.getlist('td_center_number[]')[i] +'"}'
            str = '{"locationList":[' + str +']}'
           
            
            db.session.query(User).filter_by(id = request.form['id']).update({User.name: request.form['name'], User.email: request.form['email'], User.phone: request.form['phone'], User.exam: request.form['exam'], User.dates: request.form['dates'], User.country: request.form['country'], User.locations: str}, synchronize_session = False)
            db.session.commit()
            flash('Record was successfully updated')
            return redirect(url_for('admin'))   
    else:
        user_ = User.query.filter_by(id=request.form['user_id']).first()
    user_.locations = json.loads(user_.locations)
    return render_template('user.html', form=form, user=user_)


@app.route('/del_user/<int:user_id>', methods=['GET', 'POST'])
def del_user(user_id):
    db.session.query(User).filter_by(id=user_id).delete()
    db.session.commit()

    return ""


@app.route('/view_log', methods=['POST'])
def view_log():  
    log_list = []
    try:
        log_file = open('logs/' + request.form['user_id'] + '.log', 'r') 
        while True: 
            line = log_file.readline()                
            if not line: 
                break
            if line.find("/") < 0:
                log_list.append(line.strip())                       
    except:
        pass
    return render_template('log.html', log_list = log_list)


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    return render_template('calendar.html')


@app.route('/ajax_get_countries_list/<int:examID>', methods=['GET', 'POST'])
def ajax_get_countries_list(examID):
    countries = []
    if examID == 0:
        countries = country_1.query.order_by(country_1.country)
    elif examID == 1:
        countries = country_2.query.order_by(country_2.country)
    elif examID == 2:
        countries = country_3.query.order_by(country_3.country)

    result = ""
    for country in countries:
        result += "<option value='" + country.country
        if country.country == request.args.get('country', ''):
            result += "' selected='selected"
        result += "'>" + country.country + "</option>"

    return result


@app.route('/ajax_get_user_status', methods=['GET', 'POST'])
def ajax_get_user_status():
    users = User.query.order_by(User.name)
    result = ""
    for user_ in users:
        if str(user_.id) in proxy_status:
            result += str(proxy_status[str(user_.id)]) + ","
        else:
            result += "0,"
    result = result[:-1]

    return result


@app.route('/start_proxy/<userId>', methods=['GET', 'POST'])
def start_proxy(userId):
    t_2 = MyThread_2("111")
    t_2.start()
    try:
        # if proxy_status[userId] >= 1:
        if userId in user_list:
            return ""
    except:
        pass

    proxy_status[userId] = 1
    print("proxy_status[" + userId + "] = " + str(proxy_status[userId]))
    db.session.query(User).filter_by(id = userId).update({User.status: 1}, synchronize_session = False)
    db.session.commit()

    user_ = User.query.filter_by(id=userId).first()
    user_.locations = json.loads(user_.locations)

    user_list[userId] = user_.to_dict()


    # t = MyThread(userId, user_.to_dict())
    # t.start()

    return ""
        

@app.route('/stop_proxy/<userId>', methods=['GET', 'POST'])
def stop_proxy(userId):
    proxy_status[userId] = 0
    db.session.query(User).filter_by(id = userId).update({User.status: 0}, synchronize_session = False)
    db.session.commit()
    return ""

@app.route('/api', methods=['GET', 'POST'])
def api():    
    return user_list

def status_initialize():
    db.session.query(User).update({User.status: 0}, synchronize_session = False)
    db.session.commit()
    return


def get_state_list():
    states = PostalCode.query.all()
    for state_ in states:
        state_dict[state_.state.lower()] = state_.state_code
    return

def get_proxies_list():
    if os.environ.get('FREE_PROXY') != "true":
        try:
            proxies_file = open('proxies.txt', 'r') 
            while True: 
                line = proxies_file.readline()                
                if not line: 
                    break
                proxies_list.append(line.strip())
            print("\n:::::::::::  Paid Proxy  ::::::::\n")
            return
        except:
            pass
    print("\n:::::::::::  Free Proxy  ::::::::\n")
    proxies = Proxies.query.filter_by(bad=0)
    for proxy in proxies:
        proxies_list.append(proxy.proxy)
    print(len(proxies_list))
    
    if len(proxies_list) < 50 :
        URL = 'https://github.com/TheSpeedX/PROXY-List/blob/master/http.txt'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        trs = soup.find_all(class_="blob-code blob-code-inner js-file-line")
        for tr in trs:
            if tr.get_text()[0] >= '0' and tr.get_text()[0] <= '9':
                proxies_list.append(tr.get_text())
                proxy = Proxies(tr.get_text(), 0)            
                db.session.add(proxy)
                db.session.commit()
    print(len(proxies_list))

# async def get_browser():
#     global my_browser
#     if my_browser == Null:
#         my_browser = await launch({"headless": False})
#     return my_browser 


# async def get_page(browser, url):
#     page = await browser.newPage()
#     await page.goto(url)
#     return page
    
# async def web_auto():
#     if my_browser == Null:
#         await get_browser()
#     for agency in agencies:
#         print("agency")
#         page = await get_page(my_browser, "https://securereg3.prometric.com/landing.aspx?prg=STEP1")
#         selector_str = "select[id='masterPage_cphPageBody_ddlCountry']"
#         # option = (await page.xpath("//select[@id='masterPage_cphPageBody_ddlCountry']/option[text()='CHINA']"))[0]
#         # value = await (await option.getProperty('value'))
#         # await page.select('#selectId', value);
        
#         await page.select("select[id='masterPage_cphPageBody_ddlCountry']", "CHN")
#         await page.waitFor(30000)
        


proxies_file = open('proxies.txt', 'r') 
if __name__ == '__main__':
    status_initialize()
    get_state_list()
    get_proxies_list()
    # agencies = []
    # agencies.append(Agency("111"))
    # agencies.append(Agency("222"))
    
    # temp = ""
    # temp.name = "aa" 
    # temp.user = user
    # dates = temp.user["dates"].split(",")
    # for i in range(len(dates)):
    #     dd_elem = dates[i].split("-")
    #     dates[i] = dd_elem[2] + dd_elem[1] + dd_elem[0]
    #     print("############################################")
    # dates.sort()
    # temp.user["dates"] = dates
    
    # agencies.append(Agency("222"))     
    # loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(web_auto())
    # time.sleep(5)
    # agencies.clear()
    # agencies.append(Agency("333"))
    # # agencies.append(Agency("444"))
    # result = loop.run_until_complete(web_auto())
    
    
    app.run(host='0.0.0.0', debug=True)
    