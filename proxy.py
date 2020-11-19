from asyncio.windows_events import NULL
from logging import error
import pprint
import asyncio
from pyppeteer import launch
import requests
import time
import json

users = {}
users_category = []

async def get_browser():
    return await launch({"headless": False, "defaultViewport": NULL}, args=[ '--start-maximized' ])


async def get_page(browser, exam):
    page = await browser.newPage()    
    await page.goto("https://securereg3.prometric.com/landing.aspx?prg=STEP" + str(exam + 1))
    return page


# async def extract_data(page):
#     elements = await page.xpath(
#         '//table[@class="infobox"]/tbody/tr[th and td]')
#     result = {}
#     for element in elements:
#         title, content = await page.evaluate(
#             '''(element) =>
#                 [...element.children].map(child => child.textContent)''',
#             element)
#         result.update({title: content})
#     return result


async def work(browser, exam):
    global users_category
    page = await get_page(browser, exam)
    for user_id, user in users_category[exam].items():        
        # Select Country
        # selector_str = "select[id='masterPage_cphPageBody_ddlCountry']"
        option = (await page.xpath("//select[@id='masterPage_cphPageBody_ddlCountry']/option[text()='" + user['country'] + "']"))[0]
        value = await (await option.getProperty('value')).jsonValue()
        await page.select('#masterPage_cphPageBody_ddlCountry', value) 

        # Select State
        try:
            option = (await page.xpath("//select[@id='masterPage_cphPageBody_ddlStateProvince']/option[2]"))[0]
            value = await (await option.getProperty('value')).jsonValue()
            await page.select('#masterPage_cphPageBody_ddlStateProvince', value) 
        except :
            pass

        try:
            await page.click("#masterPage_cphPageBody_btnNext")
            await page.waitFor(5000)
        except:
            pass

        try:
            await page.click("img[alt='Search for available seats']")
            await page.waitFor(10000)
        except:
            print("img error")

        try:
            for key, location_list in user["locations"].items():
                for location in location_list:
                    print("location : " + location["l"] + " , center_number : " + location["c"])
                    # if time.perf_counter() - start_time >= 1800: break  # 30 minutes - replace proxy

                    elem = await page.querySelector("span[class='bodyTitles']") 
                    text = await page.evaluate('(elem) => elem.textContent', elem)
                    if text.find("The page cannot be displayed") > -1 :
                        # my_logging(self.name, "Because this page cannot displayed, other proxy will start.")              
                        print("The page cannot be displayed")
                        raise Exception("cannot_displayed")
                    await page.waitFor(15000)
                    site_index = 0
                    # # pprint.pprint(location)
                    # my_logging(self.name, "location : " + location["l"] + " , center_number : " + location["c"])

                    # ######## break ##############
                    # if proxy_status[self.name] == 0: 
                    #     browser.close()
                    #     break

                    await page.focus('#txtSearch')
                    await page.keyboard.type(location["l"])
                    await page.waitFor(2000)
                    # elem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "txtSearch")))
                    # ######## break ##############
                    # if proxy_status[self.name] == 0: 
                    #     browser.close()
                    #     break

                    # elem.clear()
                    # elem.send_keys(location["l"])
                    # time.sleep(2)

                    await page.click("#btnSearch")
                    await page.waitFor(10000)

                    # elem, f = find_elem(False, browser, browser, "//*[@id='btnSearch']")
                    # if f == False : raise Exception("Not found element")
                    # elem.click()


                    # Confirm testcenterselection.aspx page
                    elem = await page.querySelector("#masterPage_cphPageBody_TCS_Desc1") 
                    text = await page.evaluate('(elem) => elem.textContent', elem)
                    if text.find("To find the closest location") < 0 :
                        # my_logging(self.name, "Because this page cannot displayed, other proxy will start.")              
                        print("goto redirected")
                        raise Exception("redirected")
                    else: 
                        print("no redirected")

                    # elem, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_TCS_Desc1']")
                    # if f == False : raise Exception("Not found element")
                    # elem = elem.text
                    # print(elem)
                    # if elem.find("To find the closest location") < 0 :
                    #     print("goto redirected")
                    #     my_logging(self.name, "Because this page is redirected, other proxy will start.") 
                    #     raise Exception("redirected")
                    # else: 
                    #     print("no redirected")

                    elems = await page.xpath("//tr[contains(@class,'site_row')]") 
                    print("#############")

                    # elems, f = find_elem(True, browser, browser, "//tr[contains(@class,'site_row')]")
                    # if f == False : raise Exception("Not found element")
                    # print("#############")
                    # my_logging(self.name, "Center List")

                    # Logging Center ID, Name
                    print("len = " + str(len(elems)))
                    for i in range(site_index, len(elems)):                        
                        elem_right = await elems[i].querySelector("td[class='site_row_right']") 
                        center_id = await elems[i].querySelector("td[class='site_row_left']") 
                        center_id = await page.evaluate('(center_id) => center_id.textContent', center_id)
                        center_id = center_id.splitlines()[0].split(":")[0].strip()
                        print("i = " + str(i) + ",  Center_id = " + center_id)
                    
                    #     elem_right, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_right']")
                    #     if f == False : raise Exception("Not found element")
                    #     center_id, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_left']")
                    #     if f == False : raise Exception("Not found element")
                    #     center_id = center_id.text.splitlines()[0].split(":")[0].strip()
                    #     print("Center_id = " + center_id)
                    #     my_logging(self.name, "[Center] " + center_id)

                    # my_logging(self.name, "Searching ...")

                    # ######## break ##############
                    # if proxy_status[self.name] == 0: 
                    #     browser.close()
                    #     break
                    for i in range(site_index, len(elems)):
                        elem_right = await elems[i].querySelector("td[class='site_row_right']") 
                        center_id = await elems[i].querySelector("td[class='site_row_left']") 
                        center_id = await page.evaluate('(center_id) => center_id.textContent', center_id)
                        center_id = center_id.splitlines()[0].split(":")[0].strip()
                        print("i = " + str(i) + ",  Center_id = " + center_id)
                    #     elem_right, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_right']")
                    #     if f == False : raise Exception("Not found element")
                    #     center_id, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_left']")
                    #     if f == False : raise Exception("Not found element")
                    #     center_id = center_id.text.splitlines()[0].split(":")[0].strip()
                        elem_position = await elems[i].querySelector("td[class='site_row_left']")
                        elem_position = await page.evaluate('(elem_position) => elem_position.textContent', elem_position) 
                        elem_position = " ".join(elem_position.splitlines())[:-2]
                    #     elem_position, f = find_elem(False, browser, elems[i], ".//td[@class='site_row_left']")
                    #     if f == False : raise Exception("Not found element")
                    #     elem_position = " ".join(elem_position.text.splitlines())[:-2]

                        # condition C:
                        print("location = " + str(location["c"]) + ", center_id = " + str(center_id) + ",  position = " + elem_position)
                        if location["c"] != "":
                            if location["c"].find(center_id) < 0:
                                continue
                        # Logging Center ID, Name
                        print("OK")
                        elem_availability = await elem_right.querySelector("a")
                        await elem_availability.click()
                        await page.waitFor(5000)
                    #     my_logging(self.name, "[Center] " + center_id)
                    #     elem_availability, f = find_elem(True, browser, elem_right, ".//a")
                    #     if f == False : raise Exception("Not found elem_availability")
                    #     elem_availability = elem_availability[0]
                    #     elem_availability.click()

                    #     ######## break ##############
                    #     if proxy_status[self.name] == 0: 
                    #         browser.close()
                    #         break
                    #     time.sleep(5)
                    #     ######## break ##############
                    #     if proxy_status[self.name] == 0: 
                    #         browser.close()
                    #         break
                                
                        pre_month_year = ""                            
                        sended = False                         
                        for dd in user["dates"].split(","):
                            print("date: " + dd)
                            elem_selMonthYear = await page.querySelector("#masterPage_cphPageBody_monthYearlist") 
                            month_year = str(int(dd[3:5])) + " " + dd[6:]
                            if month_year == pre_month_year:
                                continue
                    #         elem_selMonthYear, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_monthYearlist']")
                    #         if f == False : raise Exception("Not found elem_selMonthYear")
                    #         month_year = str(int(dd[4:6])) + " " + dd[:4]
                    #         if month_year == pre_month_year:
                    #             continue
                    # 30s delay
                            if not sended and pre_month_year != "":
                                await page.waitFor(5000)
                    #     ######## break ##############
                    #             if proxy_status[self.name] == 0: 
                    #                 browser.close()
                    #                 break

                            pre_month_year = month_year
                            sended = False # Flag for 30s delay
                            print("5")                                 
                            # if await page.evaluate('elem_selMonthYear.getAttribute("value")') != month_year:
                            if await ( await elem_selMonthYear.getProperty( 'value' ) ).jsonValue() != month_year:
                                print("6")

                                
                                
                        # Select month_year in list
                    #     # elem, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_monthYearlist']")
                    #     # if f == False : raise Exception("Not found element")
                                # option = (await elem_selMonthYear.xpath("/option[text()='" + month_year + "']"))[0]
                                # value = await (await option.getProperty('value')).jsonValue()
                                await page.select('#masterPage_cphPageBody_monthYearlist', month_year)
                                print("7")
                    #             select = Select(elem_selMonthYear)                                    
                    #             try:
                    #                 select.select_by_value(month_year)                                        
                    #             except:
                    #                 print("except: select month")
                    #                 continue
                    #             elem_go_btn, f = find_elem(False, browser, browser, "//*[@id='masterPage_cphPageBody_btnGoCal']")
                    #             if f == False : raise Exception("Not found elem_go_btn")
                    #             elem_go_btn.click()
                    #             time.sleep(2)
                    #     ######## break ##############
                    #             if proxy_status[self.name] == 0: 
                    #                 browser.close()
                    #                 break
                    #         elem_dates, f = find_elem(True, browser, browser, "//td[@class='calContainer'][1]//td[@onclick]")
                    #         if f == False : raise Exception("Not found elem_dates")
                    #         msg = ""
                    #         print("elem_dates")
                    #         for exam_date in elem_dates:                                        
                    #             exam_dd = int(exam_date.find_element_by_xpath(".//a").text)
                    #             print(exam_dd)
                    #             filtered_dates = [ddd for ddd in self.user["dates"] if (ddd[:6] == dd[:6] and exam_dd == int(ddd[6:]))]
                    #             print("before")
                    #             if len(filtered_dates) > 0:
                    #                 print("ok")
                    #         # SMS, email, call
                    #                 onclick_str = exam_date.get_attribute("onclick")
                    #                 onclick_str = onclick_str[onclick_str.find("(") + 1 : onclick_str.find(")")]
                    #                 onclick_str_arr = onclick_str.split(", ")
                    #                 onclick_str_date = onclick_str_arr[0][1:-1]
                    #                 onclick_str_arr = onclick_str_arr[1][1:-1].split("|")
                    #                 onclick_str_time = ", ".join(onclick_str_arr)[:-2]

                    #                 msg += onclick_str_date + "  " + onclick_str_time + "\n"
                                            
                                            
                    #                 sended = False
                                    
                    #     # print(sended)
                    #     # if msg != "":
                    #                 msg = os.environ.get('MESSAGE').replace("%NAME", self.name).replace("%DATE", onclick_str_date).replace("%TIME", onclick_str_time).replace("%LOCATION", elem_position)
                    #                 print(msg)
                    #         ######## break ##############
                    #                 if proxy_status[self.name] == 0: 
                    #                     browser.close()
                    #                     break
                                            
                    #         # msg = "Exam Place :  " + elem_position + "\nExam Date & Time :  " + msg
                    #                 my_logging(self.name, "[msg] " + msg)    
                    #         # #################### email ##############################
                    #                 try:
                    #                     smtpObj = smtplib.SMTP('smtp.gmail.com: 587')#('smtp-mail.outlook.com', 587)
                    #                 except Exception as e:
                    #                     print(e)
                    #                     my_logging(self.name, e)#'SMTP TSL connection failed.  trying SMTP SSL connection...\n' + e)
                    #                     try:
                    #                         smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    #                     except Exception as e:
                    #                         print(e)
                    #                         my_logging(self.name, 'SMTP SSL connection failed.  S M T P   F A I L E D\n' + e)
                    #                         raise Error('')
                    #                 try:
                    #                     smtpObj.ehlo()
                    #                     smtpObj.starttls()
                    #                     smtpObj.login(os.environ.get('EMAIL_ADDRESS'), os.environ.get('EMAIL_PASSWORD'))
                    #                     smtpObj.sendmail(os.environ.get('EMAIL_ADDRESS'), self.user["email"], "Subject: Notification\n" + msg)
                    #                     smtpObj.quit()
                    #                     my_logging(self.name, 'email::  to:' + self.user["email"] + ' msg: ' + msg)
                    #                     sended = True
                    #                 except Exception as e:
                    #                     print(e)
                    #                     my_logging(self.name, 'SMTP Login failed.\n' + e)
                                            
                    #         ######## break ##############
                    #                 if proxy_status[self.name] == 0: 
                    #                     browser.close()
                    #                     break
                    #         # # ################### CALL ################################
                    #                 print(twilio_phone_number)
                    #                 print("---------------------------------------------")
                    #                 print("from_=" + twilio_phone_number + ", " + " to=" + self.user["phone"] + ", " + "body=" + msg)
                    #                 try:
                    #                     response_call = client.calls.create(twiml='<Response><Say>' + msg + '</Say></Response>', from_=twilio_phone_number, to=self.user["phone"] )
                    #                     if response_call.sid :
                    #                         my_logging(self.name, 'CALL::  to:' + self.user["phone"] + ' msg: ' + msg)
                    #                         sended = True
                    #                 except  Exception as e:
                    #                     print(e)
                    #                     my_logging(self.name, e)
                                                
                    #                 print("----------------------------------------------")
                    #         ######## break ##############
                    #                 if proxy_status[self.name] == 0: 
                    #                     browser.close()
                    #                     break

                    #         # # ################### SMS ################################
                    #                 print(twilio_phone_number)
                    #                 print("---------------------------------------------")
                    #                 print("from_=" + twilio_phone_number + ", " + " to=" + self.user["phone"] + ", " + "body=" + msg)
                    #                 try:
                    #                     response_msg = client.messages.create(body=msg, from_=twilio_phone_number, to=self.user["phone"] )
                    #                     if response_msg.sid :
                    #                         my_logging(self.name, 'SMS::  to:' + self.user["phone"] + ' msg: ' + msg)
                    #                         sended = True
                    #                 except  Exception as e:
                    #                     print(e)
                    #                     my_logging(self.name, e)
                                                
                    #                 print("----------------------------------------------")

                    #         ######## break ##############
                    #                 if proxy_status[self.name] == 0: 
                    #                     browser.close()
                    #                     break
                                            
                    #                 if sended:
                    #                     proxy_status[self.name] = 2
                    #                     my_logging(self.name, "Message sent.") 
                    #                     browser.close()
                    #                     return

                    #     time.sleep(5)
                    #     ######## break ##############
                    #     if proxy_status[self.name] == 0: 
                    #         browser.close()
                    #         break
                    #     elem_go_btn = browser.find_element_by_id("masterPage_cphPageBody_btnBack")
                    #     elem_go_btn.click()
                    #     time.sleep(5)
                    #     ######## break ##############
                    #     if proxy_status[self.name] == 0: 
                    #         browser.close()
                    #         break
                    #     break

                        await page.waitFor(50000)
                    elem = await page.querySelector("span[class='bodyTitles']") 
                    text = await page.evaluate('(elem) => elem.textContent', elem)
                    print("text = " + text)
                    if text.find("The page cannot be displayed") > -1 :
                        # my_logging(self.name, "Because this page cannot displayed, other proxy will start.")              
                        raise Exception("cannot_displayed")


                    await page.waitFor(100000)
        except:
            print("error: ")
                        
        time.sleep(200)


        await page.waitFor(10000)
    await page.close()
    return


async def main():
    global users, users_category
    browser = await get_browser()
    while True:
        response = requests.get("http://localhost:5000/api")
        print(json.dumps(response.json(), sort_keys=True, indent=4))
        users = response.json()
        users_category = []
        users_category.append({})
        users_category.append({})
        users_category.append({})
        if len(users) > 0 :
            for key, user in users.items():
                users_category[user["exam"]][key] = user
                # print(user)
            for i in range(3):
                print("exam = " + str(i))
                if len(users_category[i]) > 0 :                    
                    await work(browser, i)
                    # await browser.close()

                # for key, user in users_category[i].items():
                #     print("key = " + str(key))
                #     print(user)
        else:
            time.sleep(1)
        # browser = await get_browser()
        # result = {}
        # for name, url in languages.items():
        #     result.update(await extract(browser, name, url))
        # return result


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())