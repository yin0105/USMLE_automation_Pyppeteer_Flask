# from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time , random
from threading import Thread
from os import sys
import pprint
import os
from os.path import join, dirname
from dotenv import load_dotenv
from twilio.rest import Client
import smtplib
import logging


def my_logging(f_name, msg):
    log.propagate = True
    fileh = logging.FileHandler('logs/' + f_name + '.log', 'a')
    fileh.setFormatter(formatter)
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)
    log.addHandler(fileh)
    log.debugv(msg)
    log.propagate = False


def find_elem(collection, bb, ee, xpath):
    for i in range(5):
        try:
            if collection == True:
                elem = ee.find_elements_by_xpath(xpath)
            else:
                elem = ee.find_element_by_xpath(xpath)
            return (elem, True)
        except:
            time.sleep(1)
    return (None, False) 


class MyThread(Thread):
 
    def __init__(self, name, user):
        Thread.__init__(self)
        self.name = name 
        self.user = user
        dates = self.user["dates"].split(",")
        for i in range(len(dates)):
            dd_elem = dates[i].split("-")
            dates[i] = dd_elem[2] + dd_elem[1] + dd_elem[0]
        print("############################################")
        dates.sort()
        self.user["dates"] = dates
        pprint.pprint(dates)
 
    def run(self):
        global proxies_list, proxy_index   

        while proxy_status[self.name] == 1:
            start_time = time.perf_counter()
            proxy = proxies_list[proxy_index]
            proxy_index += 1
            if proxy_index == len(proxies_list): proxy_index = 0
            is_redirected = False  # if it is true, current page is testcenterselect.aspx.

            path = '.\\Lib\\chromedriver.exe'
            options = webdriver.ChromeOptions ( ) 
            options.add_argument('--log-level=0')

            my_logging(self.name, "USE_PROXY = " + os.environ.get('USE_PROXY'))
            my_logging(self.name, "FREE_PROXY = " + os.environ.get('FREE_PROXY'))
            
            if os.environ.get('USE_PROXY') == "true":
                options.add_argument('--proxy-server=%s' % proxy)
            browser = webdriver.Chrome (executable_path = path, options = options )
            browser.get("https://securereg3.prometric.com/landing.aspx?prg=STEP" + str(self.user["exam"] + 1))
            
            my_logging(self.name, proxies_list[proxy_index] + ' started.')

            ######## break ##############
            if proxy_status[self.name] == 0: 
                browser.close()
                break
            time.sleep(5)

            ######## break ##############
            if proxy_status[self.name] == 0: 
                browser.close()
                break
            try:
                elem, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_ddlCountry']")
                if f == False : raise Exception("Not found element")
                select = Select(elem)
                select.select_by_visible_text(self.user["country"])
                my_logging(self.name, "country : " + self.user["country"])
            except:    
                my_logging(self.name, proxies_list[proxy_index] + ' is bad proxy.')               
                proxies_list.pop(proxy_index)
                proxy_index -= 1
                browser.close()
                continue
            
            ######## break ##############
            if proxy_status[self.name] == 0: 
                browser.close()
                break
            time.sleep(2)

            try:
                elem, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_ddlStateProvince']")
                if f == False : raise Exception("Not found element")
                select = Select(elem)
                select.select_by_index(1)
                time.sleep(2)
            except:
                pass

            ######## break ##############
            if proxy_status[self.name] == 0: 
                browser.close()
                break
            
            try:
                elem, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_btnNext']")
                if f == False : raise Exception("Not found element")
                elem.click()
                time.sleep(2)

                elem, f = find_elem(False, browser, browser, "//img[@alt='Search for available seats']")
                if f == False : raise Exception("Not found element")
                elem.click()

                ######## break ##############
                if proxy_status[self.name] == 0: 
                    browser.close()
                    break
                time.sleep(5)
                pprint.pprint(self.user['locations'])
            except:
                pass

            ######## break ##############
            if proxy_status[self.name] == 0: 
                browser.close()
                break

            while proxy_status[self.name] == 1 and time.perf_counter() - start_time < 1800:
                try:
                    for key, location_list in self.user["locations"].items():
                        for location in location_list:
                            print("location : " + location["l"] + " , center_number : " + location["c"])
                            if time.perf_counter() - start_time >= 1800: break  # 30 minutes - replace proxy

                            elem, f = find_elem(False, browser, browser, "//span[@class='bodyTitles']")
                            if f == False : raise Exception("Not found element")
                            elem = elem.text
                            print(elem)
                            if elem.find("The page cannot be displayed") > -1 :
                                my_logging(self.name, "Because this page cannot displayed, other proxy will start.")              
                                raise Exception("cannot_displayed")

                            site_index = 0
                            # pprint.pprint(location)
                            my_logging(self.name, "location : " + location["l"] + " , center_number : " + location["c"])

                            ######## break ##############
                            if proxy_status[self.name] == 0: 
                                browser.close()
                                break
                            elem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "txtSearch")))
                            ######## break ##############
                            if proxy_status[self.name] == 0: 
                                browser.close()
                                break

                            elem.clear()
                            elem.send_keys(location["l"])
                            time.sleep(2)

                            elem, f = find_elem(False, browser, browser, "//*[@id='btnSearch']")
                            if f == False : raise Exception("Not found element")
                            elem.click()

                            ######## break ##############
                            if proxy_status[self.name] == 0: 
                                browser.close()
                                break
                            time.sleep(10)
                            ######## break ##############
                            if proxy_status[self.name] == 0: 
                                browser.close()
                                break

                            # Confirm testcenterselection.aspx page
                            elem, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_TCS_Desc1']")
                            if f == False : raise Exception("Not found element")
                            elem = elem.text
                            print(elem)
                            if elem.find("To find the closest location") < 0 :
                                print("goto redirected")
                                my_logging(self.name, "Because this page is redirected, other proxy will start.") 
                                raise Exception("redirected")
                            else: 
                                print("no redirected")

                            elems, f = find_elem(True, browser, browser, "//tr[contains(@class,'site_row')]")
                            if f == False : raise Exception("Not found element")
                            print("#############")
                            my_logging(self.name, "Center List")

                            # Logging Center ID, Name
                            print("len = " + str(len(elems)))
                            for i in range(site_index, len(elems)):
                                print(i)
                                elem_right, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_right']")
                                if f == False : raise Exception("Not found element")
                                center_id, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_left']")
                                if f == False : raise Exception("Not found element")
                                center_id = center_id.text.splitlines()[0].split(":")[0].strip()
                                print("Center_id = " + center_id)
                                my_logging(self.name, "[Center] " + center_id)

                            my_logging(self.name, "Searching ...")

                            ######## break ##############
                            if proxy_status[self.name] == 0: 
                                browser.close()
                                break
                            for i in range(site_index, len(elems)):
                                elem_right, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_right']")
                                if f == False : raise Exception("Not found element")
                                center_id, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_left']")
                                if f == False : raise Exception("Not found element")
                                center_id = center_id.text.splitlines()[0].split(":")[0].strip()
                                elem_position, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_left']")
                                if f == False : raise Exception("Not found element")
                                elem_position = " ".join(elem_position.text.splitlines())[:-2]

                                # condition C:
                                if location["c"] != "":
                                    if center_id != location["c"]:
                                        continue
                                # Logging Center ID, Name
                                my_logging(self.name, "[Center] " + center_id)
                                elem_availability, f = find_elem(True, browser, elem_right, ".//a")
                                if f == False : raise Exception("Not found elem_availability")
                                elem_availability = elem_availability[0]
                                elem_availability.click()

                                ######## break ##############
                                if proxy_status[self.name] == 0: 
                                    browser.close()
                                    break
                                time.sleep(5)
                                ######## break ##############
                                if proxy_status[self.name] == 0: 
                                    browser.close()
                                    break
                                
                                pre_month_year = ""                            
                                
                                sended = False 
                                for dd in self.user["dates"]:
                                    elem_selMonthYear, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_monthYearlist']")
                                    if f == False : raise Exception("Not found elem_selMonthYear")
                                    month_year = str(int(dd[4:6])) + " " + dd[:4]
                                    if month_year == pre_month_year:
                                        continue
                                    # 30s delay
                                    if not sended and pre_month_year != "":
                                        time.sleep(5)
                                        ######## break ##############
                                        if proxy_status[self.name] == 0: 
                                            browser.close()
                                            break

                                    pre_month_year = month_year
                                    sended = False # Flag for 30s delay
                                                                    
                                    if elem_selMonthYear.get_attribute("value") != month_year:
                                        # Select month_year in list
                                        # elem, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_monthYearlist']")
                                        # if f == False : raise Exception("Not found element")
                                        select = Select(elem_selMonthYear)                                    
                                        try:
                                            select.select_by_value(month_year)                                        
                                        except:
                                            print("except: select month")
                                            continue
                                        elem_go_btn, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_btnGoCal']")
                                        if f == False : raise Exception("Not found elem_go_btn")
                                        elem_go_btn.click()
                                        time.sleep(2)
                                        ######## break ##############
                                        if proxy_status[self.name] == 0: 
                                            browser.close()
                                            break
                                    elem_dates, f = find_elem(True, browser, browser, "//td[@class='calContainer'][1]//td[@onclick]")
                                    if f == False : raise Exception("Not found elem_dates")
                                    msg = ""
                                    print("elem_dates")
                                    for exam_date in elem_dates:                                        
                                        exam_dd = int(exam_date.find_element_by_xpath(".//a").text)
                                        print(exam_dd)
                                        filtered_dates = [ddd for ddd in self.user["dates"] if (ddd[:6] == dd[:6] and exam_dd == int(ddd[6:]))]
                                        print("before")
                                        if len(filtered_dates) > 0:
                                            print("ok")
                                            # SMS, email, call
                                            onclick_str = exam_date.get_attribute("onclick")
                                            onclick_str = onclick_str[onclick_str.find("(") + 1 : onclick_str.find(")")]
                                            onclick_str_arr = onclick_str.split(", ")
                                            onclick_str_date = onclick_str_arr[0][1:-1]
                                            onclick_str_arr = onclick_str_arr[1][1:-1].split("|")
                                            onclick_str_time = ", ".join(onclick_str_arr)[:-2]

                                            msg += onclick_str_date + "  " + onclick_str_time + "\n"
                                            
                                            
                                            sended = False
                                    
                                        # print(sended)
                                        # if msg != "":
                                            msg = os.environ.get('MESSAGE').replace("%NAME", self.name).replace("%DATE", onclick_str_date).replace("%TIME", onclick_str_time).replace("%LOCATION", elem_position)
                                            print(msg)
                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                break
                                            
                                            # msg = "Exam Place :  " + elem_position + "\nExam Date & Time :  " + msg
                                            my_logging(self.name, "[msg] " + msg)    
                                            # #################### email ##############################
                                            try:
                                                smtpObj = smtplib.SMTP('smtp.gmail.com: 587')#('smtp-mail.outlook.com', 587)
                                            except Exception as e:
                                                print(e)
                                                my_logging(self.name, e)#'SMTP TSL connection failed.  trying SMTP SSL connection...\n' + e)
                                                try:
                                                    smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                                except Exception as e:
                                                    print(e)
                                                    my_logging(self.name, 'SMTP SSL connection failed.  S M T P   F A I L E D\n' + e)
                                                    raise Error('')
                                            try:
                                                smtpObj.ehlo()
                                                smtpObj.starttls()
                                                smtpObj.login(os.environ.get('EMAIL_ADDRESS'), os.environ.get('EMAIL_PASSWORD'))
                                                smtpObj.sendmail(os.environ.get('EMAIL_ADDRESS'), self.user["email"], "Subject: Notification\n" + msg)
                                                smtpObj.quit()
                                                my_logging(self.name, 'email::  to:' + self.user["email"] + ' msg: ' + msg)
                                                sended = True
                                            except Exception as e:
                                                print(e)
                                                my_logging(self.name, 'SMTP Login failed.\n' + e)
                                            
                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                break
                                            # # ################### CALL ################################
                                            print(twilio_phone_number)
                                            print("---------------------------------------------")
                                            print("from_=" + twilio_phone_number + ", " + " to=" + self.user["phone"] + ", " + "body=" + msg)
                                            try:
                                                response_call = client.calls.create(twiml='<Response><Say>' + msg + '</Say></Response>', from_=twilio_phone_number, to=self.user["phone"] )
                                                if response_call.sid :
                                                    my_logging(self.name, 'CALL::  to:' + self.user["phone"] + ' msg: ' + msg)
                                                    sended = True
                                            except  Exception as e:
                                                print(e)
                                                my_logging(self.name, e)
                                                
                                            print("----------------------------------------------")
                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                break

                                            # # ################### SMS ################################
                                            print(twilio_phone_number)
                                            print("---------------------------------------------")
                                            print("from_=" + twilio_phone_number + ", " + " to=" + self.user["phone"] + ", " + "body=" + msg)
                                            try:
                                                response_msg = client.messages.create(body=msg, from_=twilio_phone_number, to=self.user["phone"] )
                                                if response_msg.sid :
                                                    my_logging(self.name, 'SMS::  to:' + self.user["phone"] + ' msg: ' + msg)
                                                    sended = True
                                            except  Exception as e:
                                                print(e)
                                                my_logging(self.name, e)
                                                
                                            print("----------------------------------------------")

                                            ######## break ##############
                                            if proxy_status[self.name] == 0: 
                                                browser.close()
                                                break
                                            
                                            if sended:
                                                proxy_status[self.name] = 2
                                                my_logging(self.name, "Message sent.") 
                                                browser.close()
                                                return

                                time.sleep(5)
                                ######## break ##############
                                if proxy_status[self.name] == 0: 
                                    browser.close()
                                    break
                                elem_go_btn = browser.find_element_by_id("masterPage_cphPageBody_btnBack")
                                elem_go_btn.click()
                                time.sleep(5)
                                ######## break ##############
                                if proxy_status[self.name] == 0: 
                                    browser.close()
                                    break
                                break
                        # proxy_status[self.name] = 0
                except Exception as e:
                    time.sleep(5)
                    ######## break ##############
                    if proxy_status[self.name] == 0: 
                        browser.close()
                        break
                    print(e)
                    if e == "redirected":
                        my_logging(self.name, "Because this page is redirected, other proxy will start.") 
                    elif e == "cannot_displayed":
                        my_logging(self.name, "Because this page cannot displayed, other proxy will start.")              
                    else:
                        my_logging(self.name, proxies_list[proxy_index] + ' is bad proxy.')               
                    proxies_list.pop(proxy_index)
                    proxy_index -= 1
                    browser.close()
                    break
            
            browser.close()
            # while proxy_status[self.name] == 1:
            


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Get Twilio Account Info
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
client = Client(account_sid, auth_token)

proxies_list = []
proxy_index = 0
proxy_status = {}


formatter = logging.Formatter('%(asctime)s    %(message)s')
log = logging.getLogger()  # root logger

# log.setLevel(logging.DEBUG)
DEBUG_LEVELV_NUM = 60
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")
def debugv(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        self._log(DEBUG_LEVELV_NUM, message, args, **kws) 
logging.Logger.debugv = debugv